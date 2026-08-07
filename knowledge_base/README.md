# NutriCare AI - Knowledge Base Metadata

## Overview

The Knowledge Base is the core information repository used by the Retrieval-Augmented Generation (RAG) system in NutriCare AI.

It contains trusted medical nutrition information, recipe data, and nutritional composition data. During a user query, the RAG pipeline retrieves relevant information from this knowledge base before passing the context to the Large Language Model (LLM).

---

## Knowledge Base Structure

knowledge_base/

├── medical_knowledge/
├── recipe_database/
├── nutrition_database/

---

## Folder Description

### 1. medical_knowledge/

Purpose:
Contains evidence-based nutrition information for cancer patients collected from trusted medical organizations.

Contents:

• Cancer Nutrition
• Treatment-Based Nutrition
• Symptoms
• Nutrients
• Food Safety
• Meal Planning
• Recipe Guidelines
• FAQs
• Glossary

File Format:
Markdown (.md)

---

### 2. recipe_database/

Purpose:
Contains structured recipe information used to recommend meals based on user preferences, ingredients, symptoms, and nutritional needs.

Dataset Used:

Indian Recipes: Nutrition & Cooking Method (2026)

File Format:

CSV

Contents:

• Recipe Name
• Ingredients
• Instructions
• Cuisine
• Course
• Diet
• Preparation Time
• Cooking Time
• Serving Size
• Calories
• Protein
• Carbohydrates
• Fat
• Fiber
• Calcium
• Iron
• Vitamin C
• Sodium

---

### 3. nutrition_database/

Purpose:

Contains nutritional composition of individual food items used to calculate and display nutrition facts.

Dataset Used:

USDA FoodData Central – Foundation Foods (CSV)

File Format:

CSV

Contents:

• Food Name
• Food Category
• Calories
• Protein
• Carbohydrates
• Fat
• Fiber
• Vitamins
• Minerals
• Serving Size

---

## Data Sources

Medical Knowledge

• World Health Organization (WHO)
• National Cancer Institute (NCI)
• American Cancer Society (ACS)
• Tata Memorial Centre
• AIIMS
• National Institute of Nutrition (NIN)
• Indian Council of Medical Research (ICMR)

Recipe Database

• Indian Recipes: Nutrition & Cooking Method (2026)

Nutrition Database

• USDA FoodData Central – Foundation Foods

---

## Languages

Primary Language:
English

Future Support:
Hindi

---

## Retrieval Method

The chatbot retrieves information from:

1. Medical Knowledge
2. Recipe Database
3. Nutrition Database

The retrieved information is combined and provided to the LLM to generate the final response.

---

## Supported User Queries

The knowledge base supports queries related to:

• Cancer nutrition
• Meal planning
• Breakfast, lunch, dinner suggestions
• Ingredient-based recipe recommendations
• Nutrition facts
• Protein-rich foods
• High-calorie foods
• Hydration
• Food safety
• Symptom-based dietary guidance
• Healthy cooking methods

---

## Out of Scope

The knowledge base does not provide:

• Cancer diagnosis
• Medication recommendations
• Treatment decisions
• Medical prescriptions
• Disease prediction

---

## Last Updated

August 2026

Version: 1.0