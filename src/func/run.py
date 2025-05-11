from func.buff_tables import run


def process_args(args):
    """Processing command line arguments for functional mode"""
    print("Functional mode started with arguments:")
    print(
        f"  Directory: {args.directory_path}"
        if args.directory_path
        else f"  SQL code: {args.sql_code}"
    )
    print(f"  Separate graphs: {args.separate_graph}")
    run(
        directory=args.directory_path,
        sql_code=args.sql_code,
        separate_graph=args.separate_graph,
    )
