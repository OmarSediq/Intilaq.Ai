# core/logging_config.py

import logging
import os


def configure_logging(service_name: str):

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s - {service_name} - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/{service_name}.log"),
        ],
    )

    trace_logger = logging.getLogger(f"{service_name}.trace")
    trace_logger.setLevel(logging.INFO)

    if not trace_logger.handlers:
        trace_file = logging.FileHandler(f"logs/{service_name}_trace.log")
        trace_file.setFormatter(
            logging.Formatter(
                f"%(asctime)s - {service_name} - %(levelname)s - %(message)s"
            )
        )
        trace_logger.addHandler(trace_file)
        trace_logger.addHandler(logging.StreamHandler())
