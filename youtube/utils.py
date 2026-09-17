import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_json(file_path:Path) -> None:
    """
    JSONファイルを読み込んでPythonオブジェクトとして返す
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.exception(f"file not found: {file_path}")
    except json.JSONDecodeError as e:
        logger.exception(f"JSON parsing error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
    else:
        logger.info(f"Loaded the JSON file: {file_path}")

    return None