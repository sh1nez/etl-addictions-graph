def process_args(args):
    """Processing command line arguments for field mode"""
    print("Field mode started with arguments:")
    print(
        f"  Directory: {args.directory_path}"
        if args.directory_path
        else f"  SQL code: {args.sql_code}"
    )
    print(f"  Separate graphs: {args.separate_graph}")


def main():
    print("Hello from field mode")
