import os
from logging import Logger
from typing import List, Tuple
from base.manager import GraphManager
from base.storage import GraphStorage
from logger_config import logger  # Добавляем импорт логгера


def process_args(args):
    """Processing command line arguments for table mode"""
    manager = GraphManager()
    separate = args.separate_graph.lower() == "true"

    if args.sql_code:
        sql_code = args.sql_code
        corrections = manager.process_sql(sql_code)
        if corrections:
            logger.info("\nCorrections made:")  # Замена print на logger
            for i, correction in enumerate(corrections, 1):
                logger.info(f"{i}. {correction}")  # Замена print на logger
        manager.visualize("Dependencies Graph")
        return

    if args.directory_path:
        directory = args.directory_path
        if separate:
            parse_results = manager.parser.parse_directory(directory, sep_parse=True)
            for dependencies, corrections, file_path in parse_results:
                logger.debug(f"\nFile: {file_path}")  # Замена print на logger.debug
                if corrections:
                    logger.info("Corrections made:")  # Замена print на logger
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")  # Замена print на logger
                temp_storage = GraphStorage()
                temp_storage.add_dependencies(dependencies)
                try:
                    manager.visualizer.render(
                        temp_storage,
                        f"Dependencies for {os.path.basename(file_path)}",
                    )
                except Exception as e:
                    logger.error(
                        f"Visualization error: {e}"
                    )  # Замена print на logger.error
        else:
            results = manager.process_directory(directory)
            for file_path, corrections in results:
                logger.debug(f"\nFile: {file_path}")  # Замена print на logger.debug
                if corrections:
                    logger.info("Corrections made:")  # Замена print на logger
                    for i, correction in enumerate(corrections, 1):
                        logger.info(f"{i}. {correction}")  # Замена print на logger
            try:
                manager.visualize("Full Dependencies Graph")
            except Exception as e:
                logger.error(
                    f"Full visualization failed: {e}"
                )  # Замена print на logger.error
