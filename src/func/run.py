from func.buff_tables import run


<<<<<<< HEAD
def process_args(args):
    """Processing command line arguments for functional mode"""
    print("Functional mode started with arguments:")
    print(
        f"  Directory: {args.directory_path}"
        if args.directory_path
        else f"  SQL code: {args.sql_code}"
    )
    print(f"  Separate graphs: {args.separate_graph}")


=======
>>>>>>> 89818cf (fix: buff tables (#46))
def main():
    run()
