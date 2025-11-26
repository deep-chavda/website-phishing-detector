# feature_extractor.py
import re
import tldextract
from urllib.parse import urlparse

def is_ip_in_host(host):
    return bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host))

def count_char(s, ch):
    return s.count(ch) if isinstance(s, str) else 0

def extract_features_from_url(url):
    if not isinstance(url, str) or url.strip()=='':
        url = ''
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed = urlparse(url)
    host = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    scheme = parsed.scheme or ''
    ext = tldextract.extract(host)

    features = {}
    features['url_len'] = len(url)
    features['host_len'] = len(host)
    features['path_len'] = len(path)
    features['count_dots'] = count_char(host, '.')
    features['count_hyphen'] = count_char(host, '-')
    features['count_at'] = count_char(url, '@')
    features['count_qmark'] = count_char(url, '?')
    features['count_eq'] = count_char(url, '=')
    features['count_underscore'] = count_char(url, '_')
    features['has_ip'] = 1 if is_ip_in_host(host) else 0
    features['is_https'] = 1 if scheme == 'https' else 0
    features['tld_len'] = len(ext.suffix or '')
    suspicious_words = ['login', 'secure', 'bank', 'verify', 'update', 'free', 'signin', 'account']
    url_lower = url.lower()
    features['suspicious_word_count'] = sum(1 for w in suspicious_words if w in url_lower)
    features['num_path_tokens'] = len([tok for tok in path.split('/') if tok])
    features['num_query_tokens'] = len([tok for tok in query.split('&') if tok])
    features['dots_per_len'] = features['count_dots'] / max(1, features['host_len'])
    return features
