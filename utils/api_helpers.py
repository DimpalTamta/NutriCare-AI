# utils/api_helpers.py
import os
import requests
import urllib.parse
from googleapiclient.discovery import build

# ---------- YouTube Data API ----------
def search_youtube_video(query, api_key=None, max_results=3):
    """Return list of video IDs for a recipe query."""
    if not api_key:
        api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return []   # fallback
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query + " recipe",
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        return [item["id"]["videoId"] for item in response.get("items", [])]
    except Exception as e:
        print("YouTube API error:", e)
        return []

# ---------- Spoonacular API ----------
def get_spoonacular_recipe(query, api_key=None):
    """Fetch recipe info from Spoonacular."""
    if not api_key:
        api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return None
    try:
        url = f"https://api.spoonacular.com/recipes/complexSearch?query={urllib.parse.quote_plus(query)}&number=1&apiKey={api_key}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("results"):
                return data["results"][0]
        return None
    except Exception as e:
        print("Spoonacular error:", e)
        return None

def get_spoonacular_nutrition(food, api_key=None):
    """Get nutrition from Spoonacular for a food item."""
    if not api_key:
        api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return None
    try:
        # search ingredient
        url = f"https://api.spoonacular.com/food/ingredients/search?query={urllib.parse.quote_plus(food)}&number=1&apiKey={api_key}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("results"):
                ingredient_id = data["results"][0]["id"]
                info_url = f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/information?amount=100&unit=grams&apiKey={api_key}"
                info = requests.get(info_url, timeout=5).json()
                # Extract key nutrients
                nutrition = {
                    "name": info.get("name", food),
                    "calories": info.get("nutrition", {}).get("nutrients", [{}])[0].get("amount", "N/A") if info.get("nutrition", {}).get("nutrients") else "N/A",
                    "protein": next((n["amount"] for n in info.get("nutrition", {}).get("nutrients", []) if n["name"] == "Protein"), "N/A"),
                    "fat": next((n["amount"] for n in info.get("nutrition", {}).get("nutrients", []) if n["name"] == "Fat"), "N/A"),
                    "carbs": next((n["amount"] for n in info.get("nutrition", {}).get("nutrients", []) if n["name"] == "Carbohydrates"), "N/A"),
                }
                return nutrition
        return None
    except Exception as e:
        print("Spoonacular nutrition error:", e)
        return None

# ---------- Google Custom Search ----------
def search_ayurvedic_books(query, api_key=None, cx=None):
    """Search for Ayurvedic books online using Google Custom Search."""
    if not api_key:
        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
    if not cx:
        cx = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
    if not api_key or not cx:
        return []
    try:
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={urllib.parse.quote_plus(query)}+ayurveda+book"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return [{"title": item["title"], "link": item["link"], "snippet": item.get("snippet", "")}
                    for item in data.get("items", [])]
        return []
    except Exception as e:
        print("Custom Search error:", e)
        return []