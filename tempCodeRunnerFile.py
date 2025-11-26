# app.py
from flask import Flask, request, render_template_string, jsonify
import joblib
from train_phish_model import extract_features_from_url  # reuse extractor
import pandas as pd

app = Flask(__name__)

# Load model
data = joblib.load('models/phish_detector.joblib')
model = data['model']
feature_cols = data['feature_cols']

HTML = """
<!doctype html>
<title>Small Phishing Detector</title>
<h2>Phishing Detector</h2>
<form action="/predict" method="post">
  <input type="text" name="url" placeholder="Enter website or URL (e.g., www.google.com)" style="width:400px;">
  <input type="submit" value="Check">
</form>
{% if result is defined %}
  <h3>Result: {{ result }} (score: {{ score }})</h3>
{% endif %}
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form.get('url', '')
    feats = extract_features_from_url(url)
    X = pd.DataFrame([feats])
    X = X.reindex(columns=feature_cols, fill_value=0)
    proba = model.predict_proba(X)[0]
    # assume class order [0 legitimate, 1 phishing]
    phishing_score = float(proba[1])
    verdict = 'PHISHING' if phishing_score >= 0.5 else 'LEGIT'
    return render_template_string(HTML, result=verdict, score=f"{phishing_score:.3f}")

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json or {}
    url = data.get('url','')
    feats = extract_features_from_url(url)
    X = pd.DataFrame([feats])
    X = X.reindex(columns=feature_cols, fill_value=0)
    proba = model.predict_proba(X)[0]
    return jsonify({'url': url, 'phishing_score': proba[1], 'verdict': 'PHISHING' if proba[1]>=0.5 else 'LEGIT'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
