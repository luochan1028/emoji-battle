from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

SCORES_FILE = '/var/www/emoji-battle/scores.json'

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_scores(scores):
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

@app.route('/api/scores', methods=['POST'])
def submit_score():
    data = request.get_json()
    name = (data.get('name') or '').strip()[:12]
    score = data.get('score', 0)
    if not name:
        return jsonify({'error': 'name required'}), 400
    if not isinstance(score, int) or score < 0:
        return jsonify({'error': 'invalid score'}), 400

    entry = {
        'name': name,
        'score': score,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    scores = load_scores()
    scores.append(entry)
    scores.sort(key=lambda x: x['score'], reverse=True)
    scores = scores[:100]
    save_scores(scores)

    rank = next(i for i, s in enumerate(scores) if s['name'] == name and s['score'] == score and s['time'] == entry['time']) + 1
    return jsonify({'rank': rank, 'total': len(scores)})

@app.route('/api/scores', methods=['GET'])
def get_scores():
    scores = load_scores()
    return jsonify(scores[:20])

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
