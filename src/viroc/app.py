import io
import time

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from viroc.imaging import extract_bounding_box
from viroc.models import GOTOCRModel, YOLOModel

app = FastAPI()
detect_model = YOLOModel()
ocr_model = GOTOCRModel()


@app.post("/predict")
async def predict_image(file: UploadFile = File(...)) -> JSONResponse:
    tick = time.time()
    # Read image file
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    # Make prediction
    bb = detect_model.get_bounding_box(image)
    detection_time = time.time() - tick
    plate = extract_bounding_box(image.copy(), bb)
    generated_text = ocr_model.predict(plate)
    ocr_time = time.time() - tick - detection_time

    # Return response
    tock = time.time()
    return JSONResponse(
        {
            "license_plates": [generated_text],
            "processing_time_ms": f"{(tock - tick) * 1000:.2f}ms",
            "detection_time_ms": f"{detection_time * 1000:.2f}ms",
            "ocr_time_ms": f"{ocr_time * 1000:.2f}ms",
        }
    )
