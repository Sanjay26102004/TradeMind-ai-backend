from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Global Prediction Lock Store
prediction_locks = {}

# Mock Data: Pairs & Strategy Implementations
PAIRS_STRATEGIES = {
    'EUR/USD': 8,
    'GBP/USD': 10,
    'USD/JPY': 6,
    'AUD/USD': 9,
    'USD/CAD': 7
}

TOTAL_STRATEGIES = 10  # Total strategies in your system

@app.route('/get_pairs', methods=['POST'])
def get_pairs():
    data = request.json
    timeframe = data.get('timeframe', '')

    # Filter pairs where strategy implementations are high & checklist ≥80%
    eligible_pairs = []
    for pair, implemented_strategies in PAIRS_STRATEGIES.items():
        checklist_score = int((implemented_strategies / TOTAL_STRATEGIES) * 100)
        if checklist_score >= 80:
            eligible_pairs.append(pair)

    return jsonify({'pairs': eligible_pairs})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    pair = data.get('pair', '')
    timeframe = data.get('timeframe', '')

    # Calculate candle duration in seconds
    timeframe_seconds = {'30s': 30, '1m': 60, '5m': 300}.get(timeframe, 60)

    # Generate a unique lock key per pair-timeframe
    lock_key = f"{pair}_{timeframe}"

    current_time = datetime.utcnow()
    candle_start_time = current_time - timedelta(seconds=current_time.second % timeframe_seconds, microseconds=current_time.microsecond)
    candle_lock_expiry = candle_start_time + timedelta(seconds=timeframe_seconds)

    # Check if prediction is already given for this candle
    if lock_key in prediction_locks and prediction_locks[lock_key] > current_time:
        return jsonify({
            'message': 'Prediction already made for this candle. Wait for next candle.',
            'prediction': None,
            'checklistScore': None,
            'errorAnalysis': None,
            'lockDuration': (prediction_locks[lock_key] - current_time).seconds
        })

    # Simulate Checklist Score Calculation
    implemented_strategies = PAIRS_STRATEGIES.get(pair, 0)
    checklist_score = int((implemented_strategies / TOTAL_STRATEGIES) * 100)

    # Mock Prediction
    prediction = random.choice(['CALL', 'PUT', 'No Trade'])

    # Simulate Error Analysis on random LOSS (optional logic)
    error_analysis = None
    if random.random() < 0.2:  # Assume 20% random trade loss to show error analysis
        error_analysis = "Volume confirmation was weak in this setup. Consider filtering low-volume zones."

    # Lock prediction until candle ends
    prediction_locks[lock_key] = candle_lock_expiry

    # Ensure response returns within 5-10 sec after candle starts
    elapsed_since_candle_start = (current_time - candle_start_time).seconds
    if elapsed_since_candle_start < 5:
        wait_time = 5 - elapsed_since_candle_start
        time.sleep(wait_time)

    return jsonify({
        'prediction': prediction,
        'checklistScore': checklist_score,
        'errorAnalysis': error_analysis,
        'lockDuration': (candle_lock_expiry - current_time).seconds
    })

@app.route('/')
def home():
    return "TradeMind AI Backend is Live!"

if __name__ == '__main__':
    app.run(debug=True)
