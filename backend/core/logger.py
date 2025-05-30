import logging
import os

os.makedirs("logs", exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/intilaqai.log")
    ]
)

logger = logging.getLogger("intilaqai")

trace_logger = logging.getLogger("intilaqai.trace")
trace_logger.setLevel(logging.INFO)

trace_file_handler = logging.FileHandler("logs/trace.log")
trace_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
))

trace_logger.addHandler(trace_file_handler)
trace_logger.addHandler(logging.StreamHandler())
