import io

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
    # Read image file
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    # Make prediction
    bb = detect_model.get_bounding_box(image)
    plate = extract_bounding_box(image.copy(), bb)
    generated_text = ocr_model.predict(plate)

    # Return response
    return JSONResponse(
        {
            "license_plates": [generated_text],
        }
    )
