import cv2
import numpy as np
import kociemba

# print(kociemba.solve('FUUFUUFUURRRRRRRRRDFFDFFDFFBDDBDDBDDLLLLLLLLLBBUBBUBBU'))

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




def collect_all_faces():
    """
    Thu thập dữ liệu màu sắc từ cả 6 mặt Rubik.
    """
    face_order = ["U", "L", "F", "R", "B", "D"]
    faces = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera!")
        return None

    print("Hướng dẫn: Lần lượt đưa từng mặt của Rubik vào khung theo thứ tự U, L, F, R, B, D.")

    while len(faces) < 6:  # Lặp lại cho đến khi nhận đủ 6 mặt
        face = face_order[len(faces)]  # Chọn mặt tiếp theo để nhận diện
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Không thể đọc khung hình!")
                break

            frame = cv2.resize(frame, (640, 480))
            edges = preprocess_frame(frame)  # Tiền xử lý để phát hiện cạnh
            rubik_frame = create_rubik_frame(frame)  # Tạo khung Rubik
            rubik_detected = check_rubik_in_frame(edges, rubik_frame)  # Kiểm tra Rubik có trong khung không

            # Hiển thị cửa sổ cạnh
            cv2.imshow("Edge Detection", edges)

            if rubik_detected:
                cv2.putText(frame, f"Đặt mặt {face} vào khung và nhấn 's' để lưu!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)
                colors = detect_colors(frame, rubik_frame)

                # Hiển thị khung và màu sắc
                draw_rubik_frame(frame, rubik_frame, rubik_detected, colors)
                cv2.imshow("Rubik Detection", frame)

                if cv2.waitKey(1) & 0xFF == ord('s'):  # Nhấn 's' để lưu mặt
                    faces[face] = colors
                    print(f"Đã lưu mặt {face}")
                    break
            else:
                cv2.putText(frame, "Không phát hiện Rubik! Hãy điều chỉnh lại.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)
                cv2.imshow("Rubik Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Nhấn 'q' để thoát
                break

        # Cập nhật trạng thái các mặt đã nhận diện
        display_collected_faces_2d(faces)

    cap.release()
    cv2.destroyAllWindows()

    if len(faces) == 6:
        return faces
    else:
        print("Không nhận diện đủ 6 mặt Rubik.")
        return None


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




def create_complete_rubik_state(faces):
    """
    Tạo trạng thái Rubik đầy đủ từ dữ liệu các mặt.
    """
    # Ghép các mặt thành một chuỗi trạng thái
    rubik_state = ""
    face_order = ["U", "R", "F", "D", "L", "B"]
    for face in face_order:
        for row in faces[face]:
            for color in row:
                rubik_state += map_color_to_symbol(color)
    return rubik_state


def solve_rubik(state):
    """
    Giải Rubik bằng thư viện kociemba.
    """
    try:
        solution = kociemba.solve(state)
        return solution
    except Exception as e:
        print(f"Lỗi khi giải Rubik: {e}")
        return None

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


def preprocess_frame(frame):
    # Tiền xử lý ảnh
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    edges = cv2.Canny(gray_frame, 100, 200)
    return edges


def create_rubik_frame(frame):
    # Tạo khung Rubik
    h, w, _ = frame.shape
    size = min(h, w) // 2
    x1, y1 = (w - size) // 2, (h - size) // 2
    x2, y2 = x1 + size, y1 + size
    return (x1, y1, x2, y2)


def check_rubik_in_frame(edges, rubik_frame):
    # Kiểm tra Rubik trong khung
    x1, y1, x2, y2 = rubik_frame
    cropped_edges = edges[y1:y2, x1:x2]
    contours, _ = cv2.findContours(cropped_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) >= 9  # Kiểm tra đủ lưới 3x3


def get_color_name(hsv_pixel):
    """
    Xác định màu từ pixel HSV.
    Các ngưỡng màu được tinh chỉnh dựa trên giá trị Hue, Saturation và Value.
    """
    h, s, v = hsv_pixel
    if s < 60:  # Màu trắng
        return "White"
    elif h <= 15 :  # Màu đỏ
        return "Orange"
    elif 15 < h <= 40:  # Màu vàng
        return "Yellow"
    elif 40 < h <= 85:  # Màu xanh lá cây
        return "Green"
    elif 85 < h <= 130:  # Màu xanh dương
        return "Blue"
    elif h > 160:  # Màu cam hoặc tím
        return "Red"
    else:
        return "Unknown"


def detect_colors(frame, rubik_frame):
    """
    Nhận diện màu của từng ô Rubik.
    """
    x1, y1, x2, y2 = rubik_frame
    size = x2 - x1
    cell_size = size // 3

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    colors = []

    for i in range(3):  # Duyệt qua các hàng
        row_colors = []
        for j in range(3):  # Duyệt qua các cột
            # Tọa độ tâm của ô hiện tại
            cx = x1 + j * cell_size + cell_size // 2
            cy = y1 + i * cell_size + cell_size // 2

            # Lấy giá trị pixel HSV tại tâm
            hsv_pixel = hsv_frame[cy, cx]
            color_name = get_color_name(hsv_pixel)
            row_colors.append(color_name)

            # Vẽ ô và hiển thị màu
            cv2.circle(frame, (cx, cy), 5, (255, 255, 255), -1)
            cv2.putText(frame, color_name, (cx - 20, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        colors.append(row_colors)

    return colors


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

def construct_rubik_state(colors):
    """
    Xây dựng trạng thái Rubik từ ma trận màu sắc nhận diện.
    """
    rubik_state = ""
    for row in colors:
        for color_name in row:
            rubik_state += map_color_to_symbol(color_name)
    return rubik_state



def draw_rubik_frame(frame, rubik_frame, rubik_detected, colors=None):
    # Vẽ khung Rubik và thông báo trạng thái
    x1, y1, x2, y2 = rubik_frame
    color = (0, 255, 0) if rubik_detected else (0, 0, 255)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    # Vẽ lưới 3x3
    cell_size = (x2 - x1) // 3
    for i in range(1, 3):
        cv2.line(frame, (x1 + i * cell_size, y1), (x1 + i * cell_size, y2), color, 1)
        cv2.line(frame, (x1, y1 + i * cell_size), (x2, y1 + i * cell_size), color, 1)

    # Hiển thị thông báo trạng thái
    text = "Rubik da vao khung!" if rubik_detected else "Dua Rubik vao khung!"
    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    # Hiển thị màu sắc (nếu có)
    if colors:
        for i, row_colors in enumerate(colors):
            for j, color_name in enumerate(row_colors):
                cx = x1 + j * cell_size + cell_size // 2
                cy = y1 + i * cell_size + cell_size // 2
                cv2.putText(frame, color_name, (cx - 30, cy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


def main():
    # Nhận diện 6 mặt Rubik
    faces = collect_all_faces()
    if not faces:
        print("Không thu thập đủ thông tin Rubik.")
        return

    # Tạo trạng thái Rubik đầy đủ
    rubik_state = create_complete_rubik_state(faces)
    print(f"Trạng thái Rubik đầy đủ: {rubik_state}")

    solution = ""

    # Giải Rubik
    if validate_rubik_state(rubik_state):
        solution = solve_rubik(rubik_state)
    else:
        print("Trạng thái Rubik không hợp lệ. Kiểm tra lại nhận diện!")

    if solution:
        print(f"Bước giải: {solution}")
    else:
        print("Không thể tìm ra giải pháp.")

    # Hiển thị giải pháp trên giao diện
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể đọc khung hình!")
            break

        frame = cv2.resize(frame, (640, 480))
        display_solution_on_frame(frame, solution)

        cv2.imshow("Rubik Solution", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
