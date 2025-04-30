import os
import shutil

os.mkdir("images/train")
os.mkdir("images/val")
os.mkdir("labels/train")
os.mkdir("labels/val")

TRAIN_COUNT = 4096
TOTAL_COUNT = 5119

for i in range(0, TRAIN_COUNT):
    shutil.move(f"images/{str(i)}.png", f"images/train/{str(i)}.png")
    shutil.move(f"labels/{str(i)}.txt", f"labels/train/{str(i)}.txt")
for i in range(TRAIN_COUNT, TOTAL_COUNT + 1): 
    shutil.move(f"images/{str(i)}.png", f"images/val/{str(i)}.png")
    shutil.move(f"labels/{str(i)}.txt", f"labels/val/{str(i)}.txt")