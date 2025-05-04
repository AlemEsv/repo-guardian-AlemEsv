# src/guardian/cli.py
import sys
import argparse
from pathlib import Path
from guardian.pack_scanner import scan_pack, CrcError

def scan_command(path_str):
    repo = Path(path_str)
    try:
        scan_pack(repo)
    except CrcError as e:
        print(f"Invalid CRC at offset {e.offset}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error al escanear packfile: {e}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="CLI de Repo-Guardian")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcomando scan
    sp = subparsers.add_parser("scan", help="Escanear packfiles y objetos")
    sp.add_argument("path", help="Ruta al repositorio a escanear")

    args = parser.parse_args()

    if args.command == "scan":
        scan_command(args.path)

if __name__ == "__main__":
    main()
