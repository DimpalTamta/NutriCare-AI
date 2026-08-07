# recipe/recipe_recommender.py
from typing import Dict, List
from recipe.recipe_db import list_all_recipes
from utils.utils import get_logger

logger = get_logger(__name__)

SYMPTOM_MAP = {
    "mouth sores": ["soft", "mashed", "smoothie", "khichdi", "soup", "curd"],
    "nausea": ["ginger", "khichdi", "toast", "banana", "light", "bland"],
    "vomiting": ["light", "clear soup", "rice water", "banana"],
    "diarrhea": ["banana", "rice", "curd", "khichdi", "low fiber"],
    "constipation": ["fiber", "whole grain", "vegetable", "fruit", "oats"],
    "loss of appetite": ["small portions", "high calorie", "smoothie", "protein"],
    "taste changes": ["marinated", "tangy", "citrus", "herbs"],
    "dry mouth": ["moist", "gravy", "soup", "curry", "curd"],
    "low immunity": ["cooked vegetables", "protein", "boiled", "soup"],
    "weight loss": ["high calorie", "ghee", "nuts", "paneer", "protein"],
    "fatigue": ["protein", "iron rich", "energy", "dal", "eggs"],
    "sore throat": ["soft", "smoothie", "soup", "khichdi", "mashed"],
}

def match_symptoms(user_text: str) -> List[str]:
    user_text_lower = user_text.lower()
    return [s for s in SYMPTOM_MAP if s in user_text_lower]

def recommend_recipes(symptom_or_text: str, limit: int = 5) -> List[Dict]:
    recipes = list_all_recipes()
    if not recipes:
        return []
    matched = match_symptoms(symptom_or_text)
    if not matched:
        return recipes[:limit]
    keywords = set()
    for s in matched:
        keywords.update(SYMPTOM_MAP.get(s, []))
    scored = []
    for rec in recipes:
        haystack = " ".join([str(rec.get("recipe_name","")), str(rec.get("ingredients","")), str(rec.get("instructions",""))]).lower()
        score = sum(1 for kw in keywords if kw in haystack)
        if score > 0:
            scored.append((score, rec))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:limit]] if scored else recipes[:limit]

def list_supported_symptoms() -> List[str]:
    return list(SYMPTOM_MAP.keys())