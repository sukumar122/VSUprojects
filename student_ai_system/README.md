# AI-Based Student Academic Performance & Dropout Prediction System

## Setup Instructions

1. Install dependencies:
   pip install -r requirements.txt

2. Train the model:
   python model_training.py

3. Run the Flask app:
   python app.py

4. Test API at:
   http://127.0.0.1:5000/predict

Send POST request with JSON:
{
    "age": 20,
    "attendance": 70,
    "study_hours": 8,
    "previous_gpa": 2.5,
    "assignments_completed": 65,
    "parent_income": 35000
}
