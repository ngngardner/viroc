from pathlib import Path

import Levenshtein
import pandas as pd

results_df = pd.read_csv(
    Path(__file__).parent.parent / "results" / "benchmark_results.csv",
    dtype={
        "filename": str,
        "plate": str,
        "predicted_plate": str,
        "prediction_time_ms": float,
    },
)
print(results_df)
print(f"Average prediction time (ms): {results_df['prediction_time_ms'].mean():.2f}")
results_df["predicted_plate"] = results_df["predicted_plate"].apply(
    lambda pred: str(pred).replace("·", "")
)
results_df["correct"] = results_df["predicted_plate"] == results_df["plate"]
results_df["correct"] = results_df["correct"].astype(int)
accuracy = results_df["correct"].sum() / len(results_df)
print(f"Accuracy: {accuracy:.2%}")
results_df["levenshtein_ratio"] = results_df.apply(
    lambda row: Levenshtein.ratio(row["predicted_plate"], row["plate"]),
    axis=1,
)
print(f"Average Levenshtein ratio: {100 * results_df['levenshtein_ratio'].mean():.2f}%")
