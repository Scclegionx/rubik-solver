def map_symbol_to_bgr(symbol):
    """
    Chuyển đổi ký hiệu màu Rubik sang giá trị BGR để hiển thị.
    """
    bgr_mapping = {
        "F": (255, 255, 255),  # White
        "D": (0, 0, 255),      # Red
        "L": (0, 255, 0),      # Green
        "R": (255, 0, 0),      # Blue
        "B": (0, 255, 255),    # Yellow
        "U": (0, 165, 255),    # Orange
    }
    return bgr_mapping.get(symbol, (0, 0, 0))  # Mặc định màu đen nếu không xác định



def map_color_to_symbol(color_name):
    """
    Chuyển đổi tên màu sang ký hiệu Rubik chuẩn.
    """
    mapping = {
        "White": "F",
        "Red": "D",
        "Green": "L",
        "Blue": "R",
        "Yellow": "B",
        "Orange": "U",
    }
    return mapping.get(color_name, "?")