from pathlib import Path
import json
from typing import Any, Dict


def write_manifest(output_dir: Path, manifest: Dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def read_manifest(output_dir: Path) -> Dict[str, Any] | None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    return json.loads(manifest_path.read_text(encoding="utf-8"))
