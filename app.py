import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import streamlit as st
import requests
from PIL import Image

# 🔐 API KEY
API_KEY = "a6f8e7f144914460895286c5273aa10f"

# 🔧 Normalize text
def normalize(text):
    return text.lower().strip().rstrip('s')

# 🔧 Smart ingredient mapping (IMPORTANT)
ingredient_map = {
    "egg": ["egg", "eggs", "egg yolk", "egg yolks"],
    "milk": ["milk", "cream", "heavy cream", "whipping cream"],
    "apple": ["apple"]
}

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

# 🎨 UI
st.set_page_config(page_title="AI Kitchen", layout="centered")
st.title("🍳 AI Kitchen - Smart Recipe Feasibility System")

# Step 1: Dish input
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

        # Step 2: Upload image
        uploaded_file = st.file_uploader("Upload Refrigerator Image")

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

            # 🔁 MOCK detection (deployment-safe)
            detected_items = ["milk", "egg", "apple"]

            st.subheader("🔍 Detected Objects")
            st.write(detected_items)

            # 🔥 SMART MATCHING LOGIC
            available = []
            missing = []

            for req in recipe_ingredients:
                req_norm = normalize(req)
                found = False

                for det in detected_items:
                    det_norm = normalize(det)

                    # Check mapping (SMART MATCH)
                    if det_norm in ingredient_map:
                        for mapped_item in ingredient_map[det_norm]:
                            if mapped_item in req_norm:
                                found = True
                                break
                    # Direct partial match
                    if det_norm in req_norm:
                        found = True

                    if found:
                        break

                if found:
                    available.append(req)
                else:
                    missing.append(req)

            st.subheader("✅ Available Ingredients")
            st.write(available)

            st.subheader("❌ Missing Ingredients")
            st.write(missing)

            # 🎯 Final Result
            if len(missing) == 0:
                st.success("🎉 You can cook this recipe!")
                st.balloons()
            else:
                st.error("❌ Some ingredients are missing.")
