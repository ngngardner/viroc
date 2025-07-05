from PIL import Image, ImageDraw


def visualize_bounding_box(
    image: Image.Image, bounding_box: tuple[int, int, int, int]
) -> Image.Image:
    """
    Visualizes the bounding box on the image.

    Args:
        image (Image.Image): The input image.
        bounding_box (tuple[int, int, int, int]): The bounding box coordinates (x1, y1, x2, y2).

    Returns:
        Image.Image: The image with the bounding box drawn on it.
    """

    draw = ImageDraw.Draw(image)
    draw.rectangle(bounding_box, outline="red", width=3)
    return image
