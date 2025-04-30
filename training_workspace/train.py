# @author Saharsh S.

import ultralytics
from ultralytics import YOLO

if __name__ == '__main__':
    print(f"Using Ultralytics v{ultralytics.__version__}")

    # Nano (n), Small (s), Medium (m), Large (l), Extra Large (x)
    model = YOLO(model="last.pt") 

    model.train(data="conf.yaml", epochs=150, device="cuda", imgsz=640, patience=30, resume=True)