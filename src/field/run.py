import os
from base.manager import GraphManager
from field.storage import ColumnStorage
from logger_config import logger


def process_args(args):
    """Processing command line arguments for field mode"""
    manager = GraphManager(column_mode=True, operators=args.operators)
    separate = args.separate_graph.lower() == "true"
    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            logger.info("\nCorrections made:")
            for i, correction in enumerate(corrections, 1):
                logger.info(f"{i}. {correction}")
        manager.visualize("Dependencies Graph")
        return
    else:
        if separate:
            parse_results = manager.parser.parse_directory(
                args.directory_path, sep_parse=True
            )
            for dependencies, corrections, file_path in parse_results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
                temp_storage = ColumnStorage()
                temp_storage.add_dependencies(dependencies)
                manager.visualizer.render(
                    temp_storage,
                    f"Dependencies for {os.path.basename(file_path)}",
                )
        else:
            results = manager.process_directory(args.directory_path)
            for file_path, corrections in results:
                logger.debug(f"\nFile: {file_path}")
                if corrections:
                    logger.info("Corrections made:")
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")
            manager.visualize("Full Dependencies Graph")
            return
