from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import sqlite3
from io import BytesIO


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def init_db():
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_time TEXT,
            calorie_report TEXT,
            image BLOB,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_history(meal_time, calorie_report, image):
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO history (meal_time, calorie_report, image) VALUES (?, ?, ?)",
              (meal_time, calorie_report, image))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("user_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def get_gemini_response(input_prompt, image):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([input_prompt, image[0]])
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"


def input_image_setup(uploaded_file):
    try:
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            image_parts = [
                {
                    "mime_type": uploaded_file.type,
                    "data": bytes_data
                }
            ]
            return image_parts
        else:
            raise FileNotFoundError("No file uploaded")
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None


st.set_page_config(page_title="🌿 AiNutri", layout="wide")


init_db()

st.title(" 🌿 AiNutri")
st.write("Upload an image of your meal, and we'll estimate the calories, provide dietary advice, and more!")


with st.sidebar:
    st.header("Settings")
    meal_time = st.selectbox("Select Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack"])
    portion_size = st.radio("Select Portion Size", ["Small", "Medium", "Large"], index=1)

    st.subheader("BMI Calculator")
    weight = st.number_input("Enter your weight (kg):", min_value=1.0, format="%.2f", step=0.1)
    height = st.number_input("Enter your height (cm):", min_value=50.0, format="%.2f", step=0.1)
    age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)

    gender = st.radio("Select Gender:", ["Male", "Female"], index=0)

    activity_level = st.selectbox("Activity Level", [
        "Sedentary (little or no exercise)",
        "Lightly active (light exercise/sports 1-3 days/week)",
        "Moderately active (moderate exercise/sports 3-5 days/week)",
        "Very active (hard exercise/sports 6-7 days a week)",
        "Super active (very hard exercise/physical job)"
    ])

    dietary_preference = st.selectbox("Dietary Preference", [
        "No Preference", "Vegetarian", "Vegan", "Keto", "Low-Carb", "High-Protein"
    ])

    bmi = None

    if weight > 0 and height > 50:
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        st.write(f"### Your BMI: {bmi:.2f}")
        
        if bmi < 18.5:
            st.warning("Underweight")
        elif 18.5 <= bmi < 24.9:
            st.success("Normal weight")
        elif 25 <= bmi < 29.9:
            st.warning("Overweight")
        else:
            st.error("Obese")
    else:
        st.write("Please enter valid height and weight.")

if bmi is not None:
    diet_plan = f"""
    Diet Plan according to my BMI: {bmi:.2f}, 
    Age: {age}, 
    Gender: {gender}, 
    Weight: {weight} kg, 
    Height: {height} cm, 
    Activity Level: {activity_level}, 
    Dietary Preference: {dietary_preference}
    """
    st.write(diet_plan)






    


uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

submit = st.button("Analyze My Meal")

input_prompt = f"""
You are an expert nutritionist. Analyze the food items in the image and provide:
1. Calorie content for each item based on a {portion_size} portion.
2. A total calorie count.
3. Macronutrient breakdown (carbs, protein, fats).
4. Whether the meal is healthy, balanced, or unhealthy.
5. Suggestions for making the meal healthier and healthiear alternatives.

Format the response as:
1. Item 1 - no. of calories
2. Item 2 - no. of calories
---
Total: XX calories
Macronutrients: Carbs - Xg, Protein - Yg, Fats - Zg
Health Status: Healthy/Balanced/Unhealthy
Suggestions: ...
Diet Plan according to my BMI{bmi}, Age{age},gender{gender},weight{weight}, Height{height}, Activity level{activity_level}, Dietary preferance{dietary_preference}
Also give any allergy related issue with the item
How much time do i need to workout to burn the calories after eating item, give in bullet points
Also provide link atleast one research paper about it
"""

if submit:
    st.info("Analyzing the image... Please wait.")
    image_data = input_image_setup(uploaded_file)
    if image_data:
        response = get_gemini_response(input_prompt, image_data)
        st.success("Analysis Complete!")
        st.subheader("Results:")
        st.write(response)

        
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            image_blob = buffer.getvalue()
        save_to_history(meal_time, response, image_blob)

        
        st.download_button(
            label="Download Results as Text",
            data=response,
            file_name="calorie_report.txt",
            mime="text/plain"
        )


st.header("📜 Analysis History")
history = get_history()
if history:
    for entry in history:
        st.subheader(f"Meal Time: {entry[1]} | Date: {entry[4]}")
        st.write(entry[2])
else:
    st.write("No history available.")
