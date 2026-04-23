"""Write manifest.json into pack/ and zip it for ForeFlight import.

Runs scripts/validate_pack.py before zipping — build fails fast on any
validator-caught issue. Auto-bumps version with current UTC timestamp.

Keeps abbreviation `DDD.V1` unchanged — the pack's earlier architecture
never shipped navdata waypoints, so the switch to rich-HTML-in-layer
descriptions doesn't remove anything ForeFlight would refuse to update.
"""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
MANIFEST = PACK / "manifest.json"
ZIP_OUT = ROOT / "Diners_Drive_Ins_Dives_Pack.zip"

MAX_ZIP_BYTES = 10 * 1024 * 1024


def write_manifest() -> None:
    now = datetime.now(timezone.utc)
    version = float(now.strftime("%Y%m%d.%H%M"))
    manifest = {
        "name": "Diners, Drive-Ins and Dives",
        "abbreviation": "DDD.V1",
        "version": version,
        "effectiveDate": now.strftime("%Y%m%dT%H:%M:%SZ"),
        "organizationName": "Ingram Leedy",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {MANIFEST} (version {version})")


def zip_pack() -> int:
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(PACK.rglob("*")):
            if p.is_file() and p.name != ".gitkeep":
                arcname = p.relative_to(PACK)
                z.write(p, arcname.as_posix())
                print(f"  + {arcname.as_posix()}  ({p.stat().st_size / 1024:.1f} KB)")

    size = ZIP_OUT.stat().st_size
    print(f"zip: {ZIP_OUT} ({size / 1024:.1f} KB)")
    if size > MAX_ZIP_BYTES:
        print(f"ERROR: zip exceeds {MAX_ZIP_BYTES // (1024*1024)} MB target", file=sys.stderr)
        return 1
    return 0


def run_validator() -> int:
    validator = Path(__file__).resolve().parent / "validate_pack.py"
    if not validator.exists():
        print("WARNING: validate_pack.py not found; skipping pre-zip validation", file=sys.stderr)
        return 0
    print("running pre-zip validation...")
    return subprocess.call([sys.executable, str(validator), str(PACK)])


def main() -> int:
    write_manifest()
    if run_validator() != 0:
        print("ERROR: validator reported errors; refusing to zip. Fix and re-run.", file=sys.stderr)
        return 1
    return zip_pack()


if __name__ == "__main__":
    sys.exit(main())
