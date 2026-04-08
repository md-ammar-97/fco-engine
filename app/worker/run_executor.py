import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.core.logging import get_logger
from app.services.intake_service import load_run_inputs
from app.services.loads_service import process_loads
from app.services.city_mapping_service import build_city_mapping
from app.services.routes_service import apply_clusters_to_loads, build_routes_and_results
from app.services.fuel_service import process_fuel_prices, process_fuel_statement
from app.services.optimization_service import build_scenario_sheet
from app.services.workbook_service import write_workbook
from app.services.pdf_service import write_pdf_report
from app.services.manifest_service import write_manifest
from app.services.callback_service import post_callback
from app.worker.queue_service import get_run_record, update_run_status

logger = get_logger(__name__)


def execute_run(run_id: str) -> None:
    row = get_run_record(run_id)
    if not row:
        raise ValueError(f"Run not found: {run_id}")

    config = json.loads(row["config_json"]) if row["config_json"] else {}
    mappings = json.loads(row["mappings_json"]) if row["mappings_json"] else {}

    input_dir = Path(row["input_dir"])
    output_dir = Path(row["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    loaded = load_run_inputs(input_dir, config, mappings)
    loads = process_loads(loaded["loads"], eligibility_miles=float(config.get("eligibility_miles", 1000)))
    city_mapping = build_city_mapping(loads)
    loads = apply_clusters_to_loads(loads, city_mapping)

    fuel_prices = process_fuel_prices(loaded["fuel_prices"])
    fuel_statement, current_cpg = process_fuel_statement(loaded["fuel_statement"], fuel_prices)

    current_cpg_override = float(config.get("current_cpg_override") or 0)
    effective_cpg = current_cpg_override if current_cpg_override > 0 else current_cpg

    routes, results = build_routes_and_results(
        loads_df=loads,
        current_cpg=effective_cpg,
        decision_threshold=float(config.get("decision_threshold", 5000)),
    )

    mpg = float(config.get("assumed_mpg", 5.0))
    tank_capacity = float(config.get("tank_capacity", 240))
    ending_reserve = float(config.get("ending_fuel_reserve", 40))
    scenarios = config.get("start_fuel_scenarios", [100, 150, 180])

    avg_partner_price = fuel_prices["Partner_Price_Num"].dropna().mean() if not fuel_prices.empty else None
    scenario_unit_cost = float(avg_partner_price) if pd.notna(avg_partner_price) else float(effective_cpg or 0)

    scenario_sheets = {}
    scenario_cpgs = []
    for start_fuel in scenarios:
        scenario_df = build_scenario_sheet(
            results_df=results,
            start_fuel=float(start_fuel),
            mpg=mpg,
            tank_capacity=tank_capacity,
            ending_reserve=ending_reserve,
            unit_cost=scenario_unit_cost,
        )
        name = f"Scenario_{int(float(start_fuel))}"
        scenario_sheets[name] = scenario_df
        gallons = scenario_df["recommended_total_gallons"].sum() if not scenario_df.empty else 0.0
        cost = scenario_df["Total Cost"].sum() if not scenario_df.empty else 0.0
        scenario_cpgs.append((cost / gallons) if gallons else 0.0)

    avg_new_cpg = sum(scenario_cpgs) / len(scenario_cpgs) if scenario_cpgs else 0.0
    savings_abs = float(effective_cpg or 0) - float(avg_new_cpg or 0)
    savings_pct = ((savings_abs / float(effective_cpg)) * 100.0) if float(effective_cpg or 0) else 0.0

    final_df = pd.DataFrame([{
        "OLD_CPG": effective_cpg,
        **{f"CPG_START_{int(float(s))}": scenario_cpgs[i] if i < len(scenario_cpgs) else 0.0 for i, s in enumerate(scenarios)},
        "AVG_NEW_CPG": avg_new_cpg,
        "SAVINGS_ABS": savings_abs,
        "SAVINGS_PCT": savings_pct,
    }])

    workbook_path = output_dir / "final_workbook.xlsx"
    pdf_path = output_dir / "final_report.pdf"

    sheets = {
        "Loads": loads,
        "Fuel_Statement": fuel_statement,
        "Fuel_Prices": fuel_prices,
        "Routes": routes,
        "City_Mapping": city_mapping,
        "Results": results,
        **scenario_sheets,
        "Exceptions_Loads": loads[(loads["Eligible"] == "Yes") & (loads["Truck1"].astype(str).str.strip() == "") & (loads["Truck2"].astype(str).str.strip() == "")].copy(),
        "Exceptions_Fuel": fuel_statement[fuel_statement["Match_Status"] != "Matched"].copy(),
        "Final": final_df,
    }
    write_workbook(workbook_path, sheets)

    summary = {
        "eligible_trips": int((loads["Eligible"] == "Yes").sum()),
        "eligible_miles": float(loads.loc[loads["Eligible"] == "Yes", "Miles_Num"].sum()),
        "old_cpg": round(float(effective_cpg or 0), 4),
        "avg_new_cpg": round(float(avg_new_cpg or 0), 4),
        "savings_abs": round(float(savings_abs or 0), 4),
        "savings_pct": round(float(savings_pct or 0), 4),
    }

    write_pdf_report(
        output_path=pdf_path,
        client_name=str(config.get("client_full_name", "Client")),
        report_month=str(config.get("report_month", "")),
        summary=summary,
    )

    manifest = {
        "success": True,
        "run_id": run_id,
        "status": "completed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "message": "Step 4 preprocessing pipeline completed successfully. ORS-based optimization remains heuristic in this scaffold.",
        "workbook_path": str(workbook_path),
        "pdf_path": str(pdf_path),
        "google_sheet_url": None,
        "summary": summary,
        "exceptions": {
            "unmapped_cities": int((city_mapping["Cluster No."] == "Unresolved").sum()) if not city_mapping.empty else 0,
            "unmatched_fuel_rows": int((fuel_statement["Match_Status"] != "Matched").sum()) if not fuel_statement.empty else 0,
        },
        "error": None,
    }

    write_manifest(output_dir, manifest)

    update_run_status(run_id, "callback_pending")
    callback_ok = post_callback(
        callback_url=row["callback_url"],
        callback_token=row["callback_token"],
        payload=manifest,
    )

    if callback_ok:
        update_run_status(run_id, "completed")
    else:
        logger.warning("Callback failed for run %s; leaving status as callback_pending", run_id)
