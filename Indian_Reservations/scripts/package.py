"""Write manifest.json into the pack folder and zip it for ForeFlight import.

Emits Indian_Reservations_Pack.zip alongside the pack/ folder. Fails loudly if
the zip exceeds the 10 MB target.
"""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack"
MANIFEST = PACK / "manifest.json"
ZIP_OUT = ROOT / "Indian_Reservations_Pack.zip"

MAX_ZIP_BYTES = 10 * 1024 * 1024


def write_manifest() -> None:
    manifest = {
        "name": "Indian Reservations",
        "abbreviation": "IR.V1",
        "version": 1.0,
        "effectiveDate": datetime.now(timezone.utc).strftime("%Y%m%dT%H:%M:%SZ"),
        "organizationName": "Ingram Leedy",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {MANIFEST}")


def zip_pack() -> int:
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(PACK.rglob("*")):
            if p.is_file():
                arcname = p.relative_to(PACK)
                z.write(p, arcname.as_posix())
                print(f"  + {arcname.as_posix()}  ({p.stat().st_size / 1024:.1f} KB)")

    size = ZIP_OUT.stat().st_size
    print(f"zip: {ZIP_OUT} ({size / 1024:.1f} KB)")
    if size > MAX_ZIP_BYTES:
        print(f"ERROR: zip exceeds {MAX_ZIP_BYTES // (1024*1024)} MB target", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    write_manifest()
    return zip_pack()


if __name__ == "__main__":
    sys.exit(main())
