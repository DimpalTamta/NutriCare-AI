---
document_id: KC074
title: Recipe Recommendation Rules for Cancer Nutrition Chatbot
category: Recipe Guidelines
topic: Recipe Recommendation
description: Comprehensive rules for ranking and recommending recipes in a cancer nutrition chatbot, including nutrition matching, symptom matching, ingredient matching, personalization, and safety.
source:
  - World Health Organization (WHO)
  - National Cancer Institute (NCI)
  - American Cancer Society (ACS)
  - ESPEN
  - Stanford Health Care
language: English
version: 1.0
last_updated: 2026-08-02
keywords:
  - recipe recommendation
  - recipe ranking
  - nutrition matching
  - symptom matching
  - ingredient matching
  - personalization
  - safety rules
  - chatbot logic
---
# Recipe Recommendation Rules for Cancer Nutrition Chatbot

## Introduction
*   Nutritional care is a basic human right for all cancer patients.
*   Proper nutrition is essential before, during, and after treatment to help the body heal.
*   A chatbot must provide evidence-based guidance to help patients make informed food choices.

## Purpose of Recipe Recommendation
*   To help patients maintain a healthy weight and keep up their energy levels.
*   To provide enough protein for rebuilding body tissues harmed by treatment.
*   To manage treatment side effects that make eating difficult.

## How Recipes Should Be Ranked
*   **Weight Status:** Prioritize high-protein and high-calorie recipes for users reporting unplanned weight loss.
*   **Symptom Severity:** Rank recipes that match current symptoms (e.g., "easy to swallow") higher than regular recipes [32, Turn 2].
*   **Nutritional Density:** Rank whole-food recipes higher than those containing highly processed ingredients [Turn 4].

## Nutrition Matching Rules
*   **High-Protein:** Match to recipes containing eggs, beans, meat, or dairy to support tissue repair.
*   **High-Calorie:** Match to recipes with healthy oils, butter, or sauces for patients who are weak or underweight [29, Turn 4].
*   **Hydration:** Match to soups, smoothies, and moist foods to help meet fluid goals.

## Symptom Matching Rules
*   **Nausea:** Match to cold or room-temperature recipes with low odors [33, Turn 3].
*   **Taste Changes:** Match to recipes using herbs and mild spices to enhance bland flavors [32, Turn 3].
*   **Mouth Sores:** Match to soft, pureed, or liquid textures that are non-acidic and non-spicy [32, Turn 2, Turn 4].
*   **Dry Mouth:** Match to recipes with extra gravies, sauces, or broths [32, Turn 2].

## Treatment-Based Rules
*   **Chemotherapy:** Focus on food safety and managing metallic tastes (use non-metal utensils) [89, Turn 3, Turn 4].
*   **Radiation:** Adjust textures specifically for the area being treated (e.g., throat vs. stomach).
*   **Surgery:** Prioritize easy-to-digest recipes for the recovery period.

## Ingredient Matching Rules
*   **Pantry Staples:** Match recipes to ingredients the user already has to reduce shopping stress.
*   **Fresh Produce:** Include recipes with fruits and vegetables to support long-term health and prevention.
*   **Safe Proteins:** Ensure all recommended recipes use fully cooked meats and pasteurized dairy [Turn 4].

## Cuisine Preference Rules
*   **Cultural Variety:** Offer a wide range of global cuisines to keep the user interested in eating.
*   **Familiarity:** Allow users to save favorite cuisine types for future recommendations.

## Meal Time Matching Rules
*   **Small Portions:** Recommend "snack-sized" recipes for users who prefer small, frequent meals [Turn 3].
*   **Time of Day:** Suggest lighter recipes for breakfast and more calorie-dense options for midday meals when appetite may be higher.

## Cooking Time Preference
*   **Low Energy:** Prioritize "no-cook" or "15-minute" recipes for users experiencing treatment-related fatigue.
*   **Batch Cooking:** Suggest recipes that can be frozen and reheated later for days when energy is low.

## Difficulty Level
*   **Simple Instructions:** Use easy-to-follow steps to accommodate "chemo brain" or cognitive fatigue.
*   **Equipment:** Match recipes to the user's available tools (e.g., blender, microwave, slow cooker).

## Avoiding Restricted Foods
*   **Alcohol:** Strictly exclude recipes containing alcohol, as it is a major cancer risk factor.
*   **Raw Foods:** Exclude recipes with raw fish, raw sprouts, or undercooked eggs for immunocompromised users [Turn 4].
*   **Tobacco:** Remind users that tobacco use is a primary risk factor to avoid.

## Handling Missing Ingredients
*   **Substitutions:** Provide safe swaps (e.g., yogurt for sour cream) to maintain the calorie and protein goals.
*   **Flavor Balancing:** Suggest lemon or salt adjustments if a specific ingredient change affects the taste [Turn 3].

## Recipe Personalization
*   **Individual Needs:** Tailor recommendations based on the user's specific cancer type and treatment plan.
*   **Dietary Restrictions:** Filter out recipes that conflict with allergies or personal dietary choices (e.g., vegetarian).

## Conversation Context Usage
*   **Symptom Tracking:** If a user mentions "sore throat" earlier in the chat, the system should automatically filter for soft textures.
*   **Weight History:** If the user previously mentioned weight loss, the system should default to high-calorie suggestions.

## Image Generation Trigger
*   **Appetite Stimulation:** Generate high-quality images for recipes to help a user with a "decreased appetite" feel more like eating.
*   **Texture Visuals:** Use images to clearly show the difference between "soft," "pureed," and "liquid" levels [Turn 2].

## Nutrition Information Display
*   **Key Metrics:** Always display "Protein per serving" and "Total Calories" prominently.
*   **Simplicity:** Avoid overwhelming the user with too much data; focus on the goals set by their dietitian.

## Safety Notes
*   **Temperature:** Include a reminder to check internal cooking temperatures for safety [Turn 4].
*   **Hygiene:** Remind users to wash hands and surfaces before starting [Turn 1, Turn 4].

## Key Facts
*   Nearly 10 million people died from cancer in 2024, but many cases are curable if caught early.
*   About 38% of cancer cases can be prevented through a healthy diet and lifestyle.
*   Nutritional support can significantly improve a patient's quality of life during treatment.

## Related Topics
*   Managing specific side effects like diarrhea and constipation.
*   Long-term cancer prevention and survivorship through diet.
*   The role of exercise in improving appetite and digestion.

## References
*   World Health Organization (WHO): Cancer Fact Sheet 2026.
*   Stanford Health Care: Cancer Nutrition Services & Thrive Video Series.
*   National Cancer Institute (NCI): Comprehensive Cancer Information.
*   European Society for Clinical Nutrition and Metabolism (ESPEN): Practical Guidelines.
*   American Cancer Society (ACS): Diet and Physical Activity Guidelines.