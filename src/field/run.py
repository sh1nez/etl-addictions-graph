from base.manager import GraphManager
from base.storage import GraphStorage


def process_args(args):
    """Processing command line arguments for field mode"""
    manager = GraphManager(column_mode=True)
    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            print("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                print(f"{i}. {correction}")
    else:
        if args.separate_graph:
            parse_results = manager.parser.parse_directory(
                args.directory_path, sep_parse=True
            )
            for dependencies, corrections, file_path in parse_results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
                temp_storage = GraphStorage(column_mode=True)
                temp_storage.add_dependencies(dependencies)
        else:
            results = manager.process_directory(args.directory_path)
            for file_path, corrections in results:
                print(f"\nFile: {file_path}")
                if corrections:
                    print("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        print(f"{i}. {correction}")
