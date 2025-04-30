from ultralytics import YOLO

model = YOLO("best_140_epoch.pt")

results = model("images/val/4096.png")
# results = model("test/2.png")

results[0].show()