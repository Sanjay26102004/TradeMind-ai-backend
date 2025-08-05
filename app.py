from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import time
import random

app = Flask(__name__)
CORS(app)

# Global Prediction Lock
prediction_locks = {}

# --- Prediction Logic Function ---
def predict_next_candle(pair, timeframe, candle_data, previous_candles):
    # Dummy checklist (replace with real logic later)
    checklist = {
        "Near Key Level": random.choice([True, False]),
        "Domination Candle": random.choice([True, False]),
        "Exhaustion Candle": random.choice([True, False]),
        "Saturation Zone": random.choice([True, False]),
        "RSI Valid": random.choice([True, False]),
        "Volume Spike": random.choice([True, False]),
        "Wick Rejection": random.choice([True, False]),
        "Fake Breakout Trap": random.choice([True, False]),
        "Domination After Trap": random.choice([True, False]),
        "Range Rejection": random.choice([True, False]),
        "Clean Breakout": random.choice([True, False]),
        "Microstructure Confirmed": random.choice([True, False])
    }

    checklist_score = (sum(checklist.values()) / len(checklist)) * 100

    # Only predict if checklist score >= 80%
    if checklist_score < 80:
        return None, checklist, checklist_score

    prediction = random.choice(["CALL", "PUT"])  # Dummy logic

    return prediction, checklist, checklist_score

# --- Trade Logger ---
def log_trade_decision(log_entry):
    log_folder = "trade_logs"
    os.makedirs(log_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_folder, f"trade_{timestamp}.json")

    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=4)

# --- Error Analysis ---
def analyze_trade_error(log_entry):
    if log_entry['actual_outcome'] != 'LOSS':
        return None

    failed_conditions = [key for key, value in log_entry['checklist'].items() if value is False]
    passed_conditions = [key for key, value in log_entry['checklist'].items() if value is True]

    analysis = {
        "failed_conditions": failed_conditions,
        "passed_conditions": passed_conditions,
        "primary_reason": None,
        "suggestions": []
    }

    if 'Volume Spike' in failed_conditions or 'Microstructure Confirmed' in failed_conditions:
        analysis['primary_reason'] = 'Weak Internal Strength (Volume/Volatility Missing)'
        analysis['suggestions'].append('Ensure Volume Confirmation is prioritized in volatile markets.')

    if 'Wick Rejection' in failed_conditions and 'Near Key Level' in passed_conditions:
        analysis['primary_reason'] = 'False Key Level Rejection'
        analysis['suggestions'].append('Consider tightening wick ratio filter.')

    if 'RSI Valid' in failed_conditions:
        analysis['primary_reason'] = 'RSI Filter Ignored'
        analysis['suggestions'].append('Recheck RSI thresholds in ranging markets.')

    if not analysis['primary_reason']:
        analysis['primary_reason'] = 'Market Noise or External Factor'
        analysis['suggestions'].append('Consider checking economic calendar for news events.')

    return analysis

# --- API Route ---
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    pair = data.get('pair')
    timeframe = data.get('timeframe')
    candle_data = data.get('candle_data', {})
    previous_candles = data.get('previous_candles', [])
    actual_outcome = data.get('actual_outcome', None)

    current_time = datetime.utcnow()
    candle_key = f"{pair}_{timeframe}"
    candle_minute = current_time.minute // int(timeframe) * int(timeframe)
    candle_id = f"{current_time.strftime('%Y-%m-%d_%H')}_{candle_minute}"

    # Check if prediction for this candle is already given
    if prediction_locks.get(candle_key) == candle_id:
        return jsonify({"status": "locked", "message": "Prediction already given for current candle."})

    # Lock prediction for this candle
    prediction_locks[candle_key] = candle_id

    # Simulate delay of 5 seconds to mimic real-time processing
    time.sleep(5)

    prediction, checklist, checklist_score = predict_next_candle(pair, timeframe, candle_data, previous_candles)

    if not prediction:
        return jsonify({"status": "no_trade", "message": "Checklist accuracy below 80%.", "checklist_score": checklist_score, "checklist": checklist})

    log_entry = {
        "timestamp": current_time.isoformat(),
        "pair": pair,
        "timeframe": timeframe,
        "candle_data": candle_data,
        "previous_candles": previous_candles,
        "prediction": prediction,
        "checklist": checklist,
        "checklist_score": checklist_score,
        "actual_outcome": actual_outcome
    }

    log_trade_decision(log_entry)

    error_analysis = analyze_trade_error(log_entry) if actual_outcome == 'LOSS' else None

    return jsonify({
        "status": "success",
        "prediction": prediction,
        "checklist": checklist,
        "checklist_score": checklist_score,
        "error_analysis": error_analysis
    })

if __name__ == '__main__':
    app.run(debug=True)
