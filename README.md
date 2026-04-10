# AI Smart Farmer Assistant 🌾

A machine learning-powered crop recommendation system that helps farmers maximize profits through intelligent agricultural decision support.

## Features

- 🌾 **Crop Recommendation** - AI-powered suggestions based on soil and climate conditions
- 💰 **Profit Optimization** - Calculate expected profits for recommended crops
- 📊 **Price Prediction** - Forecast market prices and selling advice
- ⚠️ **Risk Alerts** - Real-time warnings for weather and pest risks
- 📈 **Model Confidence** - View prediction probabilities for transparency

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment on Streamlit Cloud

1. Ensure your code is pushed to GitHub repository
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub account
4. Select this repository: `Kartheek-Vk/ai-farmer-bot`
5. Select `main` branch and `app.py` as the main file
6. Click "Deploy"

## Project Structure

- `app.py` - Streamlit frontend application
- `ai_farmer_backend.py` - ML model and decision logic
- `Crop_recommendation.csv` - Training dataset
- `crop_model.pkl` - Pre-trained RandomForest model
- `requirements.txt` - Python dependencies

## Technology Stack

- **Frontend**: Streamlit
- **ML Model**: Scikit-learn RandomForestClassifier
- **Data Processing**: Pandas
- **Model Storage**: Joblib

## License

This project is licensed under the MIT License - see LICENSE file for details.