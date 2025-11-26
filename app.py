# # app.py
# from flask import Flask, request, render_template_string, jsonify
# import joblib
# from train_phish_model import extract_features_from_url  # reuse extractor
# import pandas as pd

# app = Flask(__name__)

# # Load model
# data = joblib.load('models/phish_detector.joblib')
# model = data['model']
# feature_cols = data['feature_cols']

# HTML = """
# <!doctype html>
# <title>Small Phishing Detector</title>
# <h2>Phishing Detector</h2>
# <form action="/predict" method="post">
#   <input type="text" name="url" placeholder="Enter website or URL (e.g., www.google.com)" style="width:400px;">
#   <input type="submit" value="Check">
# </form>
# {% if result is defined %}
#   <h3>Result: {{ result }} (score: {{ score }})</h3>
# {% endif %}
# """

# @app.route('/', methods=['GET'])
# def index():
#     return render_template_string(HTML)

# @app.route('/predict', methods=['POST'])
# def predict():
#     url = request.form.get('url', '')
#     feats = extract_features_from_url(url)
#     X = pd.DataFrame([feats])
#     X = X.reindex(columns=feature_cols, fill_value=0)
#     proba = model.predict_proba(X)[0]
#     # assume class order [0 legitimate, 1 phishing]
#     phishing_score = float(proba[1])
#     verdict = 'PHISHING' if phishing_score >= 0.5 else 'LEGIT'
#     return render_template_string(HTML, result=verdict, score=f"{phishing_score:.3f}")

# @app.route('/api/predict', methods=['POST'])
# def api_predict():
#     data = request.json or {}
#     url = data.get('url','')
#     feats = extract_features_from_url(url)
#     X = pd.DataFrame([feats])
#     X = X.reindex(columns=feature_cols, fill_value=0)
#     proba = model.predict_proba(X)[0]
#     return jsonify({'url': url, 'phishing_score': proba[1], 'verdict': 'PHISHING' if proba[1]>=0.5 else 'LEGIT'})

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)






# app.py  (UI-upgraded)
from flask import Flask, request, render_template_string, jsonify
import joblib
from train_phish_model import extract_features_from_url  # reuse extractor
import pandas as pd
from urllib.parse import urlparse

app = Flask(__name__)

# Load model
data = joblib.load('models/phish_detector.joblib')
model = data['model']
feature_cols = data['feature_cols']

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Phishing Detector</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(180deg,#f6f8fb 0%, #ffffff 100%); min-height:100vh; }
    .card { border-radius: 12px; box-shadow: 0 10px 30px rgba(22,37,63,0.08); }
    .logo { width:48px; height:48px; border-radius:10px; background:linear-gradient(135deg,#6f9cf3,#7de0c6); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; }
    .example-pill { cursor:pointer; }
    .small-muted { font-size:0.86rem; color:#6b7280; }
    .result-badge { font-size:1rem; padding:0.6rem 0.9rem; border-radius:10px; }
  </style>
  <script>
    function fillExample(e) {
      const v = e.getAttribute('data-url');
      document.getElementById('urlInput').value = v;
    }
    function copyScore() {
      const t = document.getElementById('scoreText').innerText;
      navigator.clipboard?.writeText(t);
      const el = document.getElementById('copyBtn');
      el.innerText = 'Copied';
      setTimeout(()=> el.innerText = 'Copy', 1200);
    }
  </script>
</head>
<body>
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-lg-8">
      <div class="card p-4">
        <div class="d-flex align-items-center mb-3">
          <div class="logo me-3">D.C</div>
          <div>
            <h4 class="mb-0">Phishing Website Detector</h4>
            <div class="small-muted">Quickly check a URL for likely phishing </div>
          </div>
          <div class="ms-auto small-muted text-end">
            <div>Model: <strong>RandomForest</strong></div>
            <div class="mt-1">Port: <strong>5000</strong></div>
          </div>
        </div>

        <!-- Form -->
        <form action="/predict" method="post" class="mb-3">
          <div class="input-group input-group-lg">
            <span class="input-group-text"><i class="bi bi-link-45deg"></i></span>
            <input id="urlInput" name="url" type="text" class="form-control" placeholder="Enter website or URL (e.g., www.google.com)" aria-label="URL" value="{{ request.form.get('url','') }}">
            <button class="btn btn-primary" type="submit">Check</button>
          </div>
          <div class="mt-2 small-muted">Tip: include protocol (https://) for best parsing. Try sample sites: 
            <span class="badge bg-light text-dark example-pill" data-url="http://example.com/login" onclick="fillExample(this)">example.com/login</span>
            <span class="badge bg-light text-dark example-pill" data-url="http://secure-bank.example.com" onclick="fillExample(this)">secure-bank.example.com</span>
          </div>
        </form>

        {% if result is defined %}
        <!-- Result area -->
        <div class="mt-3">
          <div class="d-flex align-items-center mb-2">
            <div class="me-3">
              {% if verdict == 'PHISHING' %}
                <span class="result-badge bg-danger text-white">PHISHING</span>
              {% else %}
                <span class="result-badge bg-success text-white">LEGIT</span>
              {% endif %}
            </div>
            <div class="flex-fill">
              <div class="d-flex justify-content-between mb-1">
                <div><strong>Score</strong></div>
                <div class="small-muted" id="scoreText">{{ score }}</div>
              </div>
              <div class="progress" style="height:14px; border-radius:10px;">
                {% set pct = (score_float * 100) | round(2) %}
                <div class="progress-bar {% if score_float >= 0.5 %}bg-danger{% else %}bg-success{% endif %}" role="progressbar" style="width: {{ pct }}%;" aria-valuenow="{{ pct }}" aria-valuemin="0" aria-valuemax="100">{{ pct }}%</div>
              </div>
            </div>
            <div class="ms-3">
              <button id="copyBtn" class="btn btn-outline-secondary btn-sm" type="button" onclick="copyScore()">Copy</button>
            </div>
          </div>

          <!-- Parsed components -->
          <div class="row g-2">
            <div class="col-md-6">
              <div class="card p-2">
                <div class="small-muted">Domain</div>
                <div><strong>{{ parsed.hostname }}</strong></div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card p-2">
                <div class="small-muted">Scheme</div>
                <div><strong>{{ parsed.scheme or 'http' }}</strong></div>
              </div>
            </div>
            <div class="col-md-12 mt-2">
              <div class="card p-2">
                <div class="small-muted">Full URL</div>
                <div class="text-wrap"><strong>{{ full_url }}</strong></div>
              </div>
            </div>
          </div>

        </div>
        {% endif %}

        <hr class="my-3">

        <div class="small-muted">
          <strong>How it works:</strong> Server extracts features from the URL then runs a model trained on numeric features. For production, consider HTTPS, input validation and rate-limits.
        </div>

        <div class="text-end mt-3 small-muted">
          <div>Built by Deep Chavda</div>
        </div>

      </div> <!-- card -->
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def safe_full_url(input_url):
    if not input_url:
        return ''
    if not input_url.startswith(('http://', 'https://')):
        return 'http://' + input_url
    return input_url

@app.route('/', methods=['GET'])
def index():
    return render_template_string(TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form.get('url', '') or ''
    full_url = safe_full_url(url)
    feats = extract_features_from_url(full_url)
    X = pd.DataFrame([feats])
    X = X.reindex(columns=feature_cols, fill_value=0)

    # safety: if model doesn't support predict_proba, fallback to predict
    try:
        proba = model.predict_proba(X)[0]
        phishing_score = float(proba[1])
    except Exception:
        label = int(model.predict(X)[0])
        phishing_score = 1.0 if label == 1 else 0.0

    verdict = 'PHISHING' if phishing_score >= 0.5 else 'LEGIT'
    parsed = urlparse(full_url)

    return render_template_string(
        TEMPLATE,
        result=True,
        verdict=verdict,
        score=f"{phishing_score:.3f}",
        score_float=phishing_score,
        parsed=parsed,
        full_url=full_url,
        request=request
    )

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json or {}
    url = data.get('url','') or ''
    full_url = safe_full_url(url)
    feats = extract_features_from_url(full_url)
    X = pd.DataFrame([feats])
    X = X.reindex(columns=feature_cols, fill_value=0)
    try:
        proba = model.predict_proba(X)[0]
        phishing_score = float(proba[1])
    except Exception:
        label = int(model.predict(X)[0])
        phishing_score = 1.0 if label == 1 else 0.0
    return jsonify({'url': full_url, 'phishing_score': phishing_score, 'verdict': 'PHISHING' if phishing_score >= 0.5 else 'LEGIT'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
