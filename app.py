import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import streamlit as st
import requests
from PIL import Image

# 🎯 DEMO RECIPES (SAFE)
demo_recipes = {
    "Simple Custard": ["milk", "eggs", "sugar"],
    "French Toast": ["bread", "eggs", "milk", "butter"],
    "Pancakes": ["flour", "milk", "eggs", "sugar"],
    "Bread Pudding": ["bread", "milk", "eggs", "sugar"]
}

# 🔐 API KEY
API_KEY = "a6f8e7f144914460895286c5273aa10f"

# Normalize
def normalize(text):
    return text.lower().strip().rstrip('s')

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
st.set_page_config(page_title="AI Kitchen", layout="centered")
st.title("🍳 AI Kitchen - Smart Recipe Feasibility System")

dish = st.text_input("Enter Dish Name")

if dish:

    # ✅ Toggle for demo mode
    use_demo = st.checkbox("Use Demo Recipes (Recommended for Demo)")

    if use_demo:
        choice = st.selectbox("Select Recipe", list(demo_recipes.keys()))
        recipe_ingredients = demo_recipes[choice]

    else:
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

        
       # ✅ MULTIPLE IMAGE UPLOAD (MAX 3)
uploaded_files = st.file_uploader(
    "Upload Refrigerator Images (max 3)",
    accept_multiple_files=True
)

if uploaded_files:

    # 🔴 Limit to 3 images
    if len(uploaded_files) > 3:
        st.error("You can upload maximum 3 images only.")
    else:
        all_detected = []

        # Show images + collect detections
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

            # 🔁 MOCK detection (same logic)
            detected_items = ["milk", "egg", "apple"]

            all_detected.extend(detected_items)

        # Remove duplicates
        detected_items = list(set(all_detected))

        st.subheader("🔍 AI Detected Objects")
        st.write(detected_items)

        # 🔥 HYBRID PART (USER CORRECTION)
        st.subheader("✏️ Confirm / Edit Detected Ingredients")

        manual_items = st.multiselect(
            "Adjust detected ingredients if needed:",
            ["milk", "egg", "apple", "bread", "butter", "sugar", "flour"],
            default=detected_items
        )

        detected_items = manual_items

        st.subheader("✅ Final Ingredients Used")
        st.write(detected_items)

        # 🔧 SIMPLE MATCHING
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

        st.subheader("✅ Available Ingredients")
        st.write(available)

        st.subheader("❌ Missing Ingredients")
        st.write(missing)

        # Final result
        if len(missing) == 0:
            st.success("🎉 You can cook this recipe!")
            st.balloons()
        else:
            st.error("❌ Some ingredients are missing.")
