from inference import predict_stress
from stress_relief import get_relief_actions
import argparse

def run_test(csv_path, score_override=None):
    print("Testing:", csv_path)
    score = score_override if score_override is not None else predict_stress_from_csv(csv_path)
    print(f"Stress score: {score:.3f}")

    if score > 0.5:
        print("PREDICTION: STRESSED — providing relief actions")
        actions = get_relief_actions()
        print("Music suggestions:")
        for p in (m for m in actions["music"] if m):
            name = p.get("name") or p.get("title") or "Unknown"
            url = p.get("external_urls", {}).get("spotify", "")
            print(f" - {name} -> {url}")
        print("Games:")
        for g in actions["games"]:
            # Support both string-based legacy entries and new dict entries
            if isinstance(g, dict):
                name = g.get("name", "Unnamed")
                desc = g.get("description", "")
                url = g.get("url", "")
                print(f" - {name}: {desc} -> {url}")
            else:
                print(f" - {str(g)}")
    else:
        print("PREDICTION: RELAXED — no strong action required")


def predict_stress_from_csv(path):
    import pandas as pd
    import numpy as np

    df = pd.read_csv(path)
    df = df.select_dtypes(include=[np.number]).iloc[:, :32]
    if df.shape[1] < 32:
        missing = 32 - df.shape[1]
        pad = pd.DataFrame(np.zeros((df.shape[0], missing)), index=df.index)
        df = pd.concat([df, pad], axis=1)

    eeg = df.values
    if eeg.shape[0] > eeg.shape[1]:
        eeg = eeg.T

    return predict_stress(eeg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", help="CSV file to test")
    parser.add_argument("--score", type=float, help="Override the stress score for testing (0.0-1.0)")
    args = parser.parse_args()
    run_test(args.csv, score_override=args.score)
