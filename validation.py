def validate_rubik_state(state):
    """
    Kiểm tra trạng thái Rubik có hợp lệ hay không, trả về thông báo chi tiết nếu lỗi.
    """
    from collections import Counter

    # Đếm số lượng ký hiệu trong chuỗi trạng thái
    count = Counter(state)

    # Yêu cầu số lượng mỗi ký hiệu phải là 9
    required_counts = {"F": 9, "D": 9, "L": 9, "R": 9, "B": 9, "U": 9}

    # Map từ ký hiệu sang màu để thông báo lỗi
    symbol_to_color = {
        "F": "White",
        "D": "Red",
        "L": "Green",
        "R": "Blue",
        "B": "Yellow",
        "U": "Orange",
    }

    valid = True  # Mặc định trạng thái hợp lệ

    for symbol, required in required_counts.items():
        if count[symbol] != required:
            color = symbol_to_color[symbol]
            missing = required - count[symbol]
            if missing > 0:
                print(f"Lỗi: Màu {color} thiếu {missing} ô.")
            else:
                print(f"Lỗi: Màu {color} dư {-missing} ô.")
            valid = False

    return valid