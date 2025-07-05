"""Export YOLO model to ONNX format using Hugging Face Hub."""

import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download
from rich.console import Console
from ultralytics import YOLO

console = Console()
yolo_path = Path(
    hf_hub_download(repo_id="keremberke/yolov5m-license-plate", filename="best.pt")
)
output_path = Path("deploy/models/yolo/1/model.onnx")
if not output_path.exists():
    model = YOLO(yolo_path)
    # set model parameters
    model.conf = 0.25  # NMS confidence threshold
    model.iou = 0.45  # NMS IoU threshold
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = False  # NMS multiple labels per box
    model.max_det = 1000  # maximum number of detections per image

    res = model.export(format="onnx", dynamic=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    console.log(f"Exported YOLO model to ONNX format: {res}")
    console.log(f"{yolo_path=}")
    console.log(f"{res=}")
    shutil.move(yolo_path.parent / "best.onnx", output_path)
    console.log(f"ONNX model saved to {output_path}")
else:
    console.log(f"ONNX model already exists at {output_path}")
