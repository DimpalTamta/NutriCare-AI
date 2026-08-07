# recipe/recipe_db.py
import os
import pandas as pd
from typing import Dict, List
from utils.utils import get_logger

logger = get_logger(__name__)
DEFAULT_CSV_PATH = "knowledge_base/03_Recipe_Database/Indian_Food_Ingredients_Nutrition_CookingMethods-selected-columns.csv"
_df_cache = None

def _load_df(csv_path: str = DEFAULT_CSV_PATH) -> pd.DataFrame:
    global _df_cache
    if _df_cache is not None:
        return _df_cache
    if not os.path.exists(csv_path):
        logger.error("Recipe DB not found at %s", csv_path)
        _df_cache = pd.DataFrame()
        return _df_cache
    # Adjust column names to match your CSV: recipe_original, final_food_name, etc.
    _df_cache = pd.read_csv(csv_path)
    # Rename for consistency
    _df_cache.rename(columns={
        "recipe_original": "recipe_name",
        "final_food_name": "final_name",
        "TotalTimeInMins": "total_time",
        "Cuisine": "cuisine",
        "TranslatedInstructions": "instructions",
        "TranslatedIngredients": "ingredients",
        "Cleaned-Ingredients": "cleaned_ingredients",
        "Calories (kcal)": "calories",
        "Carbohydrates (g)": "carbs",
        "Protein (g)": "protein",
    }, inplace=True)
    logger.info("Loaded recipe DB with %d recipes.", len(_df_cache))
    return _df_cache

def search_recipes(query: str, limit: int = 10) -> List[Dict]:
    df = _load_df()
    if df.empty:
        return []
    query = query.lower().strip()
    mask = (
        df["recipe_name"].str.lower().str.contains(query, na=False) |
        df["ingredients"].str.lower().str.contains(query, na=False)
    )
    return df[mask].head(limit).to_dict(orient="records")

def list_all_recipes() -> List[Dict]:
    df = _load_df()
    return df.to_dict(orient="records") if not df.empty else []