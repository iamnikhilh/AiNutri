# The Nutritionist

## Overview
The Nutritionist is a web-based application built using Streamlit that helps users analyze their meals using AI. Users can upload meal images, and the app provides a calorie breakdown, macronutrient analysis, and dietary recommendations. The results can be saved and retrieved later.

## Features
- **AI-Powered Meal Analysis**: Estimates calorie content, macronutrients, and provides health recommendations.
- **Image Upload & Processing**: Users can upload meal images for AI-driven analysis.
- **Database Storage**: Saves meal history for future reference.
- **PDF Report Generation**: Allows users to download meal analysis reports.
- **Email Report Delivery**: Sends the analysis report directly to users' emails.

## Technologies Used
- **Frontend**: Streamlit
- **Backend**: Python, Google Generative AI (Gemini Pro)
- **APIs & Libraries**:
  - SQLite (for storing meal history)
  - PIL (for image processing)
  - ReportLab (for generating PDFs)
  - SMTP (for email notifications)
- **Environment Management**: dotenv (for API keys and configurations)

