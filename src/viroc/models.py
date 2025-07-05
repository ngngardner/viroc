import cv2
import numpy as np
import torch
import tritonclient.grpc as grpcclient
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor


def preprocess_img(img: Image.Image, size: tuple[int, int]) -> np.ndarray:
    """
    Preprocess an image for model input.

    Args:
        img (Image.Image): Input image.
        size (tuple[int, int]): Target size for resizing.

    Returns:
        np.ndarray: Preprocessed image tensor.
    """
    img = cv2.resize(np.array(img), size)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return img


class TritonModel:
    """
    Base class for models.
    """

    def __init__(self, model_name: str, server_url: str) -> None:
        """
        Initialize the model with the given name and url.

        Args:
            model_name (str): Name of the model.
            server_url (str): URL of the Triton server.
        """
        self.model_name = model_name
        self.server_url = server_url
        self._client = None

    @property
    def client(self) -> grpcclient.InferenceServerClient:
        """
        Get the Triton client.

        Returns:
            Triton client instance.
        """
        if self._client is None:
            self._client = grpcclient.InferenceServerClient(url=self.server_url)
        return self._client

    def predict(self, img: Image.Image) -> np.ndarray:
        """
        Predict using the model on the input image.

        Args:
            img (Image.Image): Input image.

        Returns:
            np.ndarray: Model predictions.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class YOLOModel(TritonModel):
    """
    YOLO model class for object detection.
    """

    def __init__(
        self,
        model_name: str = "yolo",
        server_url: str = "localhost:8991",
        input_size: tuple[int, int] = (640, 640),
    ) -> None:
        """
        Initialize the YOLO model.

        Args:
            model_name (str): Name of the YOLO model.
            server_url (str): URL of the Triton server.
            input_size (tuple[int, int]): Input size for the model.
        """
        super().__init__(model_name, server_url)
        self.input_size = input_size

    def predict(self, img: Image.Image) -> np.ndarray:
        """
        Predict using the YOLO model on the input image.

        The YOLOv5 output shape is `(batch_size, num_predictions, 6)` where:
        - **batch_size**: Number of images processed (1 in this case)
        - **num_predictions**: Number of detection boxes (25200 - this includes all anchor boxes)
        - **6**: Each detection has 6 values:
        - `[0]`: x_center (center x coordinate)
        - `[1]`: y_center (center y coordinate)
        - `[2]`: width (bounding box width)
        - `[3]`: height (bounding box height)
        - `[4]`: confidence (objectness score)
        - `[5]`: class_probability (class confidence)

        Args:
            img (Image.Image): Input image.

        Returns:
            np.ndarray: Model predictions.
        """
        image_batch = preprocess_img(img, self.input_size)
        input_tensor = grpcclient.InferInput("images", image_batch.shape, "FP32")
        input_tensor.set_data_from_numpy(image_batch)
        output_tensor = grpcclient.InferRequestedOutput("output0")
        response = self.client.infer(
            model_name=self.model_name,
            inputs=[input_tensor],
            outputs=[output_tensor],
        )
        return response.as_numpy("output0")

    def get_bounding_box(self, img: Image.Image) -> tuple[int, int, int, int]:
        """
        Get the most confident bounding box from the model predictions.

        Args:
            img (Image.Image): Input image.

        Returns:
            tuple[int, int, int, int]: The most confident bounding box.
        """
        prediction = self.predict(img)[0]
        most_confident_box = prediction[prediction[:, 4].argmax()]

        original_width, original_height = img.size
        model_width, model_height = self.input_size
        x_center, y_center, width, height = most_confident_box[:4]
        scale_x = original_width / model_width
        scale_y = original_height / model_height
        x1 = int((x_center - width / 2) * scale_x)
        y1 = int((y_center - height / 2) * scale_y)
        x2 = int((x_center + width / 2) * scale_x)
        y2 = int((y_center + height / 2) * scale_y)
        return (x1, y1, x2, y2)

    def get_bounding_boxes(
        self,
        img: Image.Image,
        threshold: float,
        overlap_tolerance: float = 0.05,
    ) -> list[tuple[int, int, int, int]]:
        """
        Get the top bounding boxes from the model predictions filtered by a confidence threshold.

        Args:
            img (Image.Image): Input image.
            threshold (float): Confidence threshold.
            overlap_tolerance (float): Tolerance for overlapping boxes.

        Returns:
            list[tuple[int, int, int, int]]: List of bounding boxes.
        """
        predictions = self.predict(img)[0]
        sorted_boxes = predictions[predictions[:, 4].argsort()[::-1]]
        sorted_boxes = sorted_boxes[sorted_boxes[:, 4] > threshold]
        original_width, original_height = img.size
        model_width, model_height = self.input_size
        scale_x = original_width / model_width
        scale_y = original_height / model_height

        boxes = []
        for box in sorted_boxes:
            x_center, y_center, width, height = box[:4]
            x1 = int((x_center - width / 2) * scale_x)
            y1 = int((y_center - height / 2) * scale_y)
            x2 = int((x_center + width / 2) * scale_x)
            y2 = int((y_center + height / 2) * scale_y)
            boxes.append((x1, y1, x2, y2))

        # filter duplicate boxes (they may have some overlap)
        filtered_boxes = []
        for box in boxes:
            x1, y1, x2, y2 = box
            if not any(
                (
                    abs(x1 - f_x1) < overlap_tolerance * original_width
                    and abs(y1 - f_y1) < overlap_tolerance * original_height
                    and abs(x2 - f_x2) < overlap_tolerance * original_width
                    and abs(y2 - f_y2) < overlap_tolerance * original_height
                )
                for f_x1, f_y1, f_x2, f_y2 in filtered_boxes
            ):
                filtered_boxes.append(box)
        return filtered_boxes


class GOTOCRModel:
    """"""

    def __init__(self) -> None:
        """
        Initialize the GOTOCR model.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForImageTextToText.from_pretrained(
            "stepfun-ai/GOT-OCR-2.0-hf",
            device_map=self.device,
        )
        self.processor = AutoProcessor.from_pretrained(
            "stepfun-ai/GOT-OCR-2.0-hf", use_fast=True
        )

    def predict(self, img: Image.Image) -> str:
        """
        Predict using the GOTOCR model on the input image.

        Args:
            img (Image.Image): Input image.

        Returns:
            str: Model predictions.
        """
        inputs = self.processor(images=img, return_tensors="pt").to(self.device)
        generate_ids = self.model.generate(
            **inputs,
            do_sample=False,
            tokenizer=self.processor.tokenizer,
            stop_strings="<|im_end|>",
            max_new_tokens=4096,
        )
        return str(
            self.processor.decode(
                generate_ids[0, inputs["input_ids"].shape[1] :],
                skip_special_tokens=True,
            )
        )
