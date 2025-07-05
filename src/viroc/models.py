import cv2
import numpy as np
import tritonclient.grpc as grpcclient
from PIL import Image


def preprocess_img(img: Image.Image, size: tuple[int, int] = (640, 640)) -> np.ndarray:
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
        self, model_name: str = "yolo", server_url: str = "localhost:8991"
    ) -> None:
        """
        Initialize the YOLO model.

        Args:
            model_name (str): Name of the YOLO model.
            server_url (str): URL of the Triton server.
        """
        super().__init__(model_name, server_url)

    def predict(self, img: Image.Image) -> np.ndarray:
        """
        Predict using the YOLO model on the input image.

        Args:
            img (Image.Image): Input image.

        Returns:
            np.ndarray: Model predictions.
        """
        image_batch = preprocess_img(img)
        input_tensor = grpcclient.InferInput("images", image_batch.shape, "FP32")
        input_tensor.set_data_from_numpy(image_batch)
        output_tensor = grpcclient.InferRequestedOutput("output0")
        response = self.client.infer(
            model_name=self.model_name,
            inputs=[input_tensor],
            outputs=[output_tensor],
        )
        return response.as_numpy("output0")
