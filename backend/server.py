# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import numpy as np
# from inference import predict_stress
# from stress_relief import get_relief_actions

# app = Flask(__name__)
# CORS(app)

# @app.route("/predict", methods=["POST"])
# def predict():
#     eeg = np.array(request.json["eeg"])
#     score = predict_stress(eeg)
#     if score > 0.5:
#         return jsonify({"stress": True, "score": score, "relief": get_relief_actions()})
#     return jsonify({"stress": False, "score": score})

# app.run(port=5000)
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from inference import predict_stress
from stress_relief import get_relief_actions

app = Flask(__name__)
CORS(app)

@app.route("/predict", methods=["POST"])
def predict():
    eeg = np.array(request.json["eeg"])

    # Predict stress probability (0–1)
    score = predict_stress(eeg)

    # 🔑 REALISTIC EEG INTERPRETATION
    if score < 0.4:
        state = "RELAXED"
        stress = False
        relief = None

    elif score < 0.7:
        state = "MILD STRESS"
        stress = True
        relief = {
            "message": "Light relaxation recommended",
            "actions": get_relief_actions(state)
        }

    else:
        state = "HIGH STRESS"
        stress = True
        relief = {
            "message": "Strong stress detected",
            "actions": get_relief_actions(state)
        }

    return jsonify({
        "stress": stress,
        "stress_level": state,
        "score": float(score),
        "relief": relief
    })

if __name__ == "__main__":
    app.run(port=5000, debug=False)
