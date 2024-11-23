import cv2

def check_rubik_in_frame(edges, rubik_frame):
    # Kiểm tra Rubik trong khung
    x1, y1, x2, y2 = rubik_frame
    cropped_edges = edges[y1:y2, x1:x2]
    contours, _ = cv2.findContours(cropped_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) >= 9  # Kiểm tra đủ lưới 3x3

def preprocess_frame(frame, use_threshold=True, threshold_method='adaptive'):
    """
    Tiền xử lý ảnh: Chuyển đổi sang xám, cân bằng histogram, làm mờ và phát hiện cạnh.
    """
    # Chuyển sang ảnh xám
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Cân bằng histogram
    gray_frame = cv2.equalizeHist(gray_frame)

    # Làm mờ ảnh để giảm nhiễu
    gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Áp dụng Thresholding
    if use_threshold:
        if threshold_method == 'binary':
            _, gray_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        elif threshold_method == 'adaptive':
            gray_frame = cv2.adaptiveThreshold(
                gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        cv2.imshow("Thresholding", gray_frame)

    # Phát hiện cạnh bằng Canny
    edges = cv2.Canny(gray_frame, 100, 200)

    return edges


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

def histogram_equalization(image):
    if len(image.shape) == 2:  # Grayscale
        return cv2.equalizeHist(image)
    elif len(image.shape) == 3:  # Color image
        channels = cv2.split(image)
        eq_channels = [cv2.equalizeHist(ch) for ch in channels]
        return cv2.merge(eq_channels)