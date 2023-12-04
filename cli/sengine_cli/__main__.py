import argparse
from pathlib import Path
from sonic_engine.core.engine import Engine
import yaml

def start_cli(config_file, show_logs=False):
    print("CLI started! OHO\n")
    if show_logs:
        print("Showing logs\n!")

    # engine = Engine((__file__, config_file))
    # engine.start()
    print(config_file)
    
def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="command")

    start_parser = subparser.add_parser("start")

    start_parser.add_argument('config_file')
    start_parser.add_argument('-l', '--logs', action="store_true")

    args = parser.parse_args()
    target_config_file = Path(args.config_file)

    if args.command == "start":
        if not target_config_file.exists():
            print("Config file does not exist!")
            raise SystemExit(1)
        start_cli(target_config_file, args.logs)
    else:
        parser.print_help()
        

if __name__ == "__main__":
    main()
