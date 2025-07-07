"""
Script to decode CCPD dataset labels from filenames.
The labels are embedded in the filenames according to the format specified in README.md
"""


def decode_ccpd_filename(filename):
    """
    Decode CCPD filename to extract all label information.

    Format: [area]-[tilt_deg]-[bbox]-[vertices]-[lp_number]-[brightness]-[blurriness].jpg

    Args:
        filename: CCPD filename (e.g., "025-95_113-154&383_386&473-386&473_177&454_154&383_363&402-0_0_22_27_27_33_16-37-15.jpg")

    Returns:
        dict: Decoded label information
    """
    # Remove extension and split by '-'
    base_name = filename.replace(".jpg", "")
    parts = base_name.split("-")

    if len(parts) < 7:
        print(f"Warning: Filename {filename} doesn't match expected format")
        return None

    # Parse each component
    area = parts[0]
    tilt_degrees = parts[1].split("_")  # horizontal_vertical
    bbox_coords = parts[2].split("_")  # x1,y1_x2,y2
    vertices = parts[3].split("_")  # Four vertices coordinates
    lp_number = parts[4].split("_")  # License plate characters
    brightness = parts[5]
    blurriness = parts[6]

    # Character mapping for license plate
    provinces = [
        "皖",
        "沪",
        "津",
        "渝",
        "冀",
        "晋",
        "蒙",
        "辽",
        "吉",
        "黑",
        "苏",
        "浙",
        "京",
        "闽",
        "赣",
        "鲁",
        "豫",
        "鄂",
        "湘",
        "粤",
        "桂",
        "琼",
        "川",
        "贵",
        "云",
        "藏",
        "陕",
        "甘",
        "青",
        "宁",
        "新",
        "警",
        "学",
        "O",
    ]
    alphabets = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "J",
        "K",
        "L",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "O",
    ]
    ads = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "J",
        "K",
        "L",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "O",
    ]

    # Decode license plate characters
    decoded_lp = ""
    if len(lp_number) == 7:
        try:
            decoded_lp += provinces[int(lp_number[0])]  # Province
            decoded_lp += alphabets[int(lp_number[1])]  # City letter
            for i in range(2, 7):  # 5 alphanumeric characters
                decoded_lp += ads[int(lp_number[i])]
        except (IndexError, ValueError):
            decoded_lp = "Error decoding"

    # Parse bounding box coordinates
    bbox_parsed = None
    if len(bbox_coords) == 2:
        try:
            x1, y1 = map(int, bbox_coords[0].split(","))
            x2, y2 = map(int, bbox_coords[1].split(","))
            bbox_parsed = [x1, y1, x2, y2]
        except ValueError:
            bbox_parsed = "Error parsing bbox"

    # Parse four vertices
    vertices_parsed = []
    for vertex in vertices:
        try:
            x, y = map(int, vertex.split(","))
            vertices_parsed.append([x, y])
        except ValueError:
            vertices_parsed.append("Error parsing vertex")

    return {
        "area_ratio": area,
        "tilt_horizontal": tilt_degrees[0] if len(tilt_degrees) > 0 else None,
        "tilt_vertical": tilt_degrees[1] if len(tilt_degrees) > 1 else None,
        "bbox": bbox_parsed,
        "vertices": vertices_parsed,
        "license_plate": decoded_lp,
        "lp_numbers_raw": lp_number,
        "brightness": brightness,
        "blurriness": blurriness,
    }
