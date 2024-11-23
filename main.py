import cv2
from validation import validate_rubik_state
from solution import solve_rubik
from display import *
from map import *
from image_processing import *

# print(kociemba.solve('FUUFUUFUURRRRRRRRRDFFDFFDFFBDDBDDBDDLLLLLLLLLBBUBBUBBU'))

def create_rubik_frame(frame):
    # Tạo khung Rubik
    h, w, _ = frame.shape
    size = min(h, w) // 2
    x1, y1 = (w - size) // 2, (h - size) // 2
    x2, y2 = x1 + size, y1 + size
    return x1, y1, x2, y2

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
