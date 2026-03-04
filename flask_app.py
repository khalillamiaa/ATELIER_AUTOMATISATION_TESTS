from flask import Flask, render_template, jsonify, request
import sqlite3
import os
import datetime
import sys
sys.path.append(os.path.dirname(__file__))
from tester.runner import run_tests

app = Flask(__name__)

# Chemin vers la base de données SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'runs.db')

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                api TEXT,
                passed INTEGER,
                failed INTEGER,
                error_rate REAL,
                latency_avg REAL,
                latency_p95 REAL,
                details TEXT
            )
        ''')
init_db()

@app.route('/')
def index():
    return render_template('consignes.html')

@app.route('/run')
def run():
    result = run_tests()
    # Sauvegarde en base
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT INTO runs (timestamp, api, passed, failed, error_rate, latency_avg, latency_p95, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result['timestamp'],
            result['api'],
            result['summary']['passed'],
            result['summary']['failed'],
            result['summary']['error_rate'],
            result['summary']['latency_ms_avg'],
            result['summary']['latency_ms_p95'],
            json.dumps(result['tests'])
        ))
    return jsonify(result)

@app.route('/dashboard')
def dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute('SELECT * FROM runs ORDER BY timestamp DESC LIMIT 10')
        runs = cursor.fetchall()
    return render_template('dashboard.html', runs=runs)

if __name__ == '__main__':
    app.run(debug=True)
