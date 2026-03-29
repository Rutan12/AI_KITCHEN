import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import streamlit as st
import requests
from PIL import Image

# Spoonacular API
API_KEY = "YOUR_API_KEY"

# Fetch recipes
def get_recipes(query):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {"query": query, "number": 5, "apiKey": API_KEY}
    res = requests.get(url, params=params).json()
    return res.get("results", [])

# Fetch ingredients
def get_ingredients(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": API_KEY}
    res = requests.get(url, params=params).json()
    return [i['name'] for i in res.get('extendedIngredients', [])]

# UI
st.title("🍳 AI Kitchen - Smart Recipe Feasibility System")

dish = st.text_input("Enter Dish Name")

if dish:
    recipes = get_recipes(dish)

    if len(recipes) == 0:
        st.error("No recipes found")

    else:
        recipe_titles = [r['title'] for r in recipes]
        choice = st.selectbox("Select Recipe", recipe_titles)

        recipe_id = recipes[recipe_titles.index(choice)]['id']
        recipe_ingredients = get_ingredients(recipe_id)

        st.subheader("🧾 Required Ingredients")
        st.write(recipe_ingredients)

        # Upload image
        uploaded_file = st.file_uploader("Upload Refrigerator Image")

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

            # MOCK detection
            detected_items = ["milk", "egg", "apple"]

            st.subheader("🔍 Detected Objects")
            st.write(detected_items)

            detected_set = set(detected_items)
            required_set = set(recipe_ingredients)

            available = detected_set.intersection(required_set)
            missing = required_set - detected_set

            st.subheader("✅ Available Ingredients")
            st.write(list(available))

            st.subheader("❌ Missing Ingredients")
            st.write(list(missing))
