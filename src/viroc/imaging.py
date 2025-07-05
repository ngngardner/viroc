from PIL import Image, ImageDraw


def visualize_bounding_box(
    img: Image.Image, bounding_box: tuple[int, int, int, int]
) -> Image.Image:
    """
    Visualizes the bounding box on the image.

    Args:
        img (Image.Image): The input image.
        bounding_box (tuple[int, int, int, int]): The bounding box coordinates (x1, y1, x2, y2).

    Returns:
        Image.Image: The image with the bounding box drawn on it.
    """

    draw = ImageDraw.Draw(img)
    draw.rectangle(bounding_box, outline="red", width=3)
    return img


def extract_bounding_box(
    img: Image.Image, bounding_box: tuple[int, int, int, int]
) -> Image.Image:
    """
    Extracts the region of interest defined by the bounding box from the image.

    Args:
        img (Image.Image): The input image.
        bounding_box (tuple[int, int, int, int]): The bounding box coordinates (x1, y1, x2, y2).

    Returns:
        Image.Image: The cropped image defined by the bounding box.
    """
    return img.crop(bounding_box)
