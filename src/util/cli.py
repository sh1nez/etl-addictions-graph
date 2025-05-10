import argparse


def parse_arguments():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser(
        description="SQL Syntax Corrector and Dependency Analyzer"
    )

    parser.add_argument(
        "--mode",
        choices=["table", "field", "functional"],
        required=True,
        help="Program operation mode: table, field or functional",
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--directory_path",
        type=str,
        help="Path to the directory containing SQL files for processing",
    )
    source_group.add_argument(
        "--sql_code", type=str, help="SQL code for direct processing"
    )

    parser.add_argument(
        "--separate_graph",
        choices=["true", "false"],
        default="false",
        help="Display graphs separately for each file",
    )
    parser.add_argument(
        "--operators",
        type=str,
        help="Comma-separated list of SQL operators to display (e.g., 'SELECT,INSERT,UPDATE'). "
        "If not specified, all operators are shown.",
    )
    return parser.parse_args()
