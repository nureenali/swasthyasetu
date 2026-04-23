import cv2

def load_image(image_path: str):
    return cv2.imread(image_path)

def preprocess_for_ocr(image):
    h, w = image.shape[:2]

    max_width = 900
    if w > max_width:
        new_h = int((max_width / w) * h)
        image = cv2.resize(image, (max_width, new_h))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray