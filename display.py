import cv2
import numpy as np
from map import *


def display_collected_faces_2d(faces):
    """
    Hiển thị trạng thái Rubik dưới dạng 2D Net (trải phẳng).
    """
    # Kích thước mỗi ô vuông
    cube_size = 50
    # Canvas trắng đủ lớn để chứa toàn bộ các mặt Rubik
    canvas_height = cube_size * 12  # 9 hàng + khoảng trắng
    canvas_width = cube_size * 12  # 12 cột
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

    # Định nghĩa vị trí các mặt trong cấu trúc 2D
    face_positions = {
        "U": (1, 3),  # Mặt trên (U)
        "L": (4, 0),  # Mặt trái (L)
        "F": (4, 3),  # Mặt trước (F)
        "R": (4, 6),  # Mặt phải (R)
        "B": (4, 9),  # Mặt sau (B)
        "D": (7, 3),  # Mặt dưới (D)
    }

    for face, (row_offset, col_offset) in face_positions.items():
        if face in faces:
            for i, row_colors in enumerate(faces[face]):
                for j, color_name in enumerate(row_colors):
                    # Tính tọa độ từng ô vuông
                    x1 = (col_offset + j) * cube_size
                    y1 = (row_offset + i) * cube_size
                    x2 = x1 + cube_size
                    y2 = y1 + cube_size

                    # Lấy màu BGR tương ứng
                    color_bgr = map_symbol_to_bgr(map_color_to_symbol(color_name))

                    # Vẽ ô vuông với màu tương ứng
                    cv2.rectangle(canvas, (x1, y1), (x2, y2), color_bgr, -1)
                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 1)  # Viền đen

    # Hiển thị Rubik 2D Net
    cv2.imshow("Rubik 2D Net", canvas)
    cv2.waitKey(1)


def display_solution_on_frame(frame, solution):
    """
    Hiển thị bước giải Rubik trên giao diện.
    """
    if solution:
        steps = solution.split()
        instructions = " -> ".join(steps)
        cv2.putText(frame, "Solution:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, instructions, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)
    else:
        cv2.putText(frame, "No solution available.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)