## Phishing URL Detector

A simple Flask-based web app that detects whether a URL is PHISHING or LEGIT using a Machine Learning model.
Includes a clean Bootstrap UI and a JSON API.

## Features

URL Phishing detection using RandomForest ML model

Bootstrap-based clean UI

Probability score shown with progress bar

REST API endpoint /api/predict

Extracts URL-based features automatically

Easy to run locally

## Project Structure
app.py                  # Flask UI + API
train_phish_model.py    # Training script + URL feature extractor
models/phish_detector.joblib
dataset_phishing.csv
README.md

## Setup
Install dependencies
pip install flask pandas numpy scikit-learn joblib tldextract

Train model (optional)
python train_phish_model.py

Run the app
python app.py


App runs at: localhost

## API Example
Request
POST /api/predict
{
  "url": "http://secure-login-example.com/verify"
}

Response
{
  "url": "http://secure-login-example.com/verify",
  "phishing_score": 0.91,
  "verdict": "PHISHING"
}

 ##License

MIT — free to use and modify.
