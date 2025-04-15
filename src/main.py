import sys

import field.run
import func.run
import table.run
from util.cli import parse_arguments


def main():
    """Main function that processes command line arguments"""
    args = parse_arguments()

    if args.mode == "table":
        table.run.process_args(args)
    elif args.mode == "field":
        field.run.process_args(args)
    elif args.mode == "functional":
        func.run.process_args(args)
    else:
        print(f"Error: Unknown mode {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
