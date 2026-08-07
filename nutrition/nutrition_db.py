# nutrition/nutrition_db.py
import os
import pandas as pd
from difflib import get_close_matches
from typing import Dict, List, Optional
from utils.utils import get_logger

logger = get_logger(__name__)
DEFAULT_CSV_PATH = "knowledge_base/02_Nutrition_Database/indian_food_database.csv"
_df_cache = None

def _load_df(csv_path: str = DEFAULT_CSV_PATH) -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    if not os.path.exists(csv_path):
        logger.error("Nutrition DB not found at %s", csv_path)
        _df_cache = pd.DataFrame()
        return _df_cache
    # 🔥 FIX: use latin-1 encoding to handle special characters
    _df_cache = pd.read_csv(csv_path, encoding='latin-1')
    _df_cache["food_name_lower"] = _df_cache["food_name"].str.lower().str.strip()
    logger.info("Loaded nutrition DB with %d foods.", len(_df_cache))
    return _df_cache

def search_food(query: str, limit: int = 5) -> List[str]:
    df = _load_df()
    if df.empty:
        return []
    query = query.lower().strip()
    substring = df[df["food_name_lower"].str.contains(query, na=False)]
    names = list(substring["food_name"].unique())[:limit]
    if len(names) < limit:
        close = get_close_matches(query, df["food_name_lower"].tolist(), n=limit, cutoff=0.6)
        for c in close:
            match_row = df[df["food_name_lower"] == c].iloc[0]
            if match_row["food_name"] not in names:
                names.append(match_row["food_name"])
    return names[:limit]

def get_nutrition(food_name: str) -> Optional[Dict]:
    df = _load_df()
    if df.empty:
        return None
    query = food_name.lower().strip()
    exact = df[df["food_name_lower"] == query]
    if exact.empty:
        candidates = search_food(query, limit=1)
        if not candidates:
            return None
        exact = df[df["food_name"] == candidates[0]]
    if exact.empty:
        return None
    return exact.iloc[0].to_dict()