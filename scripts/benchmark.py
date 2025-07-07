import time

import pandas as pd
import tqdm
from PIL import Image

from viroc.dataset import dataset_path
from viroc.decode_ccpd_labels import decode_ccpd_filename
from viroc.imaging import extract_bounding_box
from viroc.models import GOTOCRModel, YOLOModel

detect_model = YOLOModel()
ocr_model = GOTOCRModel()


def predict_plates(img: Image.Image) -> list[str]:
    bbs = detect_model.get_bounding_boxes(img, threshold=0.05, overlap_tolerance=0.30)
    plates = []
    for i, bb in enumerate(bbs):
        plate = extract_bounding_box(img, bb)
        plates.append(ocr_model.predict(plate))

    return plates


valid_file = dataset_path.parent / "splits" / "val.txt"
with valid_file.open("r") as f:
    valid_files = f.read().splitlines()

valid_df = pd.DataFrame(valid_files, columns=["filename"])
valid_df = valid_df.sample(5000, random_state=42)
valid_df["filename"] = valid_df["filename"].apply(lambda fn: dataset_path.parent / fn)
valid_df["plate"] = valid_df["filename"].apply(
    lambda fn: decode_ccpd_filename(str(fn.name))["license_plate"]
)
preds = []
pred_times = []
for _, row in tqdm.tqdm(valid_df.iterrows(), total=len(valid_df)):
    tick = time.time()
    img = Image.open(row["filename"])
    plate = predict_plates(img)
    preds.append(plate[0] if plate else None)
    pred_times.append((time.time() - tick) * 1000)
valid_df["predicted_plate"] = preds
valid_df["prediction_time_ms"] = pred_times
valid_df.to_csv("benchmark_results.csv", index=False)
print("Benchmark results saved to benchmark_results.csv")
