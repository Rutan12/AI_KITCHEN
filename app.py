import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import streamlit as st
import requests
from PIL import Image

# 🔐 API KEY
API_KEY = "a6f8e7f144914460895286c5273aa10f"

# 🎯 DEMO RECIPES
demo_recipes = {
    "Simple Custard": ["milk", "eggs", "sugar"],
    "French Toast": ["bread", "eggs", "milk", "butter"],
    "Pancakes": ["flour", "milk", "eggs", "sugar"],
    "Bread Pudding": ["bread", "milk", "eggs", "sugar"]
}

# Normalize
def normalize(text):
    return text.lower().strip().rstrip('s')

# API functions
def get_recipes(query):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {"query": query, "number": 5, "apiKey": API_KEY}
    res = requests.get(url, params=params).json()
    return res.get("results", [])

def get_ingredients(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": API_KEY}
    res = requests.get(url, params=params).json()
    return [i['name'] for i in res.get('extendedIngredients', [])]

# 🎨 UI SETTINGS
st.set_page_config(page_title="AI Kitchen", layout="wide", page_icon="🍳")

st.markdown("""
# 🍳 AI Kitchen  
### Smart Recipe Feasibility System
---
""")

# INPUT
dish = st.text_input("Enter Dish Name")

if dish:

    # DEMO MODE
    use_demo = st.checkbox("Use Demo Recipes")

    if use_demo:
        choice = st.selectbox("Select Recipe", list(demo_recipes.keys()))
        recipe_ingredients = demo_recipes[choice]
    else:
        recipes = get_recipes(dish)

        if len(recipes) == 0:
            st.error("No recipes found")
            st.stop()

        recipe_titles = [r['title'] for r in recipes]
        choice = st.selectbox("Select Recipe", recipe_titles)

        recipe_id = recipes[recipe_titles.index(choice)]['id']
        recipe_ingredients = get_ingredients(recipe_id)

    # INGREDIENTS
    st.markdown("---")
    st.subheader("🧾 Required Ingredients")

    for item in recipe_ingredients:
        st.write(f"• {item}")

    # MULTIPLE IMAGE UPLOAD
    uploaded_files = st.file_uploader(
        "Upload Refrigerator Images (max 3)",
        accept_multiple_files=True
    )

    if uploaded_files:

        if len(uploaded_files) > 3:
            st.error("You can upload maximum 3 images only.")
            st.stop()

        st.markdown("---")
        st.subheader("📸 Uploaded Images")

        cols = st.columns(len(uploaded_files))

        all_detected = []

        for i, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file)
            cols[i].image(image, caption=f"Image {i+1}")

            # MOCK DETECTION
            detected_items = ["milk", "egg", "apple"]
            all_detected.extend(detected_items)

        detected_items = list(set(all_detected))

        st.markdown("---")
        st.subheader("🔍 AI Detected Objects")
        st.write(detected_items)

        # USER CORRECTION
        st.subheader("✏️ Confirm / Edit Ingredients")

        manual_items = st.multiselect(
            "Adjust detected ingredients:",
            ["milk", "egg", "apple", "bread", "butter", "sugar", "flour"],
            default=detected_items
        )

        detected_items = manual_items

        st.subheader("✅ Final Ingredients Used")
        st.write(detected_items)

        # MATCHING LOGIC
        available = []
        missing = []

        for req in recipe_ingredients:
            req_norm = normalize(req)

            if (
                "egg" in req_norm and "egg" in detected_items
            ) or (
                "milk" in detected_items and ("milk" in req_norm or "cream" in req_norm)
            ) or (
                "apple" in detected_items and "apple" in req_norm
            ) or (
                "bread" in detected_items and "bread" in req_norm
            ) or (
                "butter" in detected_items and "butter" in req_norm
            ) or (
                "sugar" in detected_items and "sugar" in req_norm
            ) or (
                "flour" in detected_items and "flour" in req_norm
            ):
                available.append(req)
            else:
                missing.append(req)

        # RESULTS
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Available Ingredients")
            for item in available:
                st.write(f"✔ {item}")

        with col2:
            st.subheader("❌ Missing Ingredients")
            for item in missing:
                st.write(f"✖ {item}")

        # SUMMARY
        st.markdown("---")
        st.subheader("📊 Summary")

        col1, col2 = st.columns(2)
        col1.metric("Available", len(available))
        col2.metric("Missing", len(missing))

        # FINAL MESSAGE
        if len(missing) == 0:
            st.success("All required ingredients are available.")
        else:
            st.warning("Some ingredients are missing.")
