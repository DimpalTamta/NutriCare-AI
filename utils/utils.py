# utils/utils.py
import os
import json
import logging
import datetime
from pathlib import Path
from typing import Any, Optional

def get_logger(name: str = "nutricare") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def safe_read_text(path: str, encoding: str = "utf-8") -> str:
    try:
        with open(path, "r", encoding=encoding, errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def safe_write_text(path: str, content: str, encoding: str = "utf-8") -> bool:
    try:
        ensure_dir(str(Path(path).parent))
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False

def list_files(directory: str, extensions: Optional[list] = None) -> list:
    result = []
    if not os.path.isdir(directory):
        return result
    for root, _, files in os.walk(directory):
        for fname in files:
            if extensions is None or Path(fname).suffix.lower() in extensions:
                result.append(os.path.join(root, fname))
    return result

def timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.datetime.now().strftime(fmt)

def save_json(path: str, data: Any) -> bool:
    try:
        ensure_dir(str(Path(path).parent))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def load_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def truncate(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[:max_len].rstrip() + "..."