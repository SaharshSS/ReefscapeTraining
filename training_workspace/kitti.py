#!/usr/bin/env python2

from PIL import Image
import argparse
import os
import csv

OUT_LABELS_DIR = "labels"

SINDEX = 2

KEY_ALGAE = "algae"
KEY_ALGAE_BARGE = "algaebarge"
KEY_ALGAE_LOW = "algaelow"
KEY_ALGAE_HIGH = "algaehigh"
KEY_CORAL = "coral"
KEY_CORAL_L1 = "corall1"
KEY_CORAL_L2 = "corall2"
KEY_CORAL_L3 = "corall3"
KEY_CORAL_L4 = "corall4"
KEY_CAGE = "cage"
KEY_CORALSTATION = "coralstation"
KEY_REEF = "reef"

CLAZZ_NUMBERS = {
        KEY_ALGAE: 0 + SINDEX,
        KEY_ALGAE_BARGE: 1 + SINDEX,
        KEY_ALGAE_LOW: 2 + SINDEX,
        KEY_ALGAE_HIGH: 3 + SINDEX,
        KEY_CORAL: 4 + SINDEX,
        KEY_CORAL_L1: 5 + SINDEX,
        KEY_CORAL_L2: 6 + SINDEX,
        KEY_CORAL_L3: 7 + SINDEX,
        KEY_CORAL_L4: 8 + SINDEX,
        KEY_CAGE: 9 + SINDEX,
        KEY_CORALSTATION: 10 + SINDEX,
        KEY_REEF: 11 + SINDEX
    }

def resolveClazzNumberOrNone(clazz):
    if clazz == KEY_ALGAE:
        return CLAZZ_NUMBERS[KEY_ALGAE]
    if clazz == KEY_ALGAE_BARGE:
        return CLAZZ_NUMBERS[KEY_ALGAE_BARGE]
    if clazz == KEY_ALGAE_LOW:
        return CLAZZ_NUMBERS[KEY_ALGAE_LOW]
    if clazz == KEY_ALGAE_HIGH:
        return CLAZZ_NUMBERS[KEY_ALGAE_HIGH]
    if clazz == KEY_CORAL:
        return CLAZZ_NUMBERS[KEY_CORAL]
    if clazz == KEY_CORAL_L1:
        return CLAZZ_NUMBERS[KEY_CORAL_L1]
    if clazz == KEY_CORAL_L2:
        return CLAZZ_NUMBERS[KEY_CORAL_L2]
    if clazz == KEY_CORAL_L3:
        return CLAZZ_NUMBERS[KEY_CORAL_L3]
    if clazz == KEY_CORAL_L4:
        return CLAZZ_NUMBERS[KEY_CORAL_L4]
    if clazz == KEY_CAGE:
        return CLAZZ_NUMBERS[KEY_CAGE]
    if clazz == KEY_CORALSTATION:
        return CLAZZ_NUMBERS[KEY_CORALSTATION]
    if clazz == KEY_REEF:
        return CLAZZ_NUMBERS[KEY_REEF]
    return None

def getSampleId(path):
    basename = os.path.basename(path)
    return os.path.splitext(basename)[0]

def convertToYoloBBox(bbox, size):
    # Yolo uses bounding bbox coordinates and size relative to the image size.
    # This is taken from https://pjreddie.com/media/files/voc_label.py .
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (bbox[0] + bbox[1]) / 2.0
    y = (bbox[2] + bbox[3]) / 2.0
    w = bbox[1] - bbox[0]
    h = bbox[3] - bbox[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def readRealImageSize(img_path):
    # This loads the whole sample image and returns its size.
    return Image.open(img_path).size

def readFixedImageSize():
    # This is not exact for all images but most (and it should be faster).
    return (512, 512)

def parseSample(lbl_path, img_path):
    with open(lbl_path) as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=["type", "truncated", "occluded", "alpha", "bbox2_left", "bbox2_top", "bbox2_right", "bbox2_bottom", "bbox3_height", "bbox3_width", "bbox3_length", "bbox3_x", "bbox3_y", "bbox3_z", "bbox3_yaw", "score"], delimiter=" ")
        yolo_labels = []
        for row in reader:
            clazz_number = resolveClazzNumberOrNone(row["type"])
            if clazz_number is not None:
                size = readRealImageSize(img_path)
                #size = readFixedImageSize()
                # Image coordinate is in the top left corner.
                bbox = (
                        float(row["bbox2_left"]),
                        float(row["bbox2_right"]),
                        float(row["bbox2_top"]),
                        float(row["bbox2_bottom"])
                       )
                yolo_bbox = convertToYoloBBox(bbox, size)
                # Yolo expects the labels in the form:
                # <object-class> <x> <y> <width> <height>.
                yolo_label = (clazz_number,) + yolo_bbox
                yolo_labels.append(yolo_label)
    return yolo_labels

def parseArguments():
    parser = argparse.ArgumentParser(description="Generates labels for training darknet on KITTI.")
    # parser.add_argument("label_dir", help="data_object_label_2/training/label_2 directory; can be downloaded from KITTI.")
    # parser.add_argument("image_2_dir", help="data_object_image_2/training/image_2 directory; can be downloaded from KITTI.")
    parser.add_argument("--training-samples", type=int, default=0.8, help="percentage of the samples to be used for training between 0.0 and 1.0.")
    parser.add_argument("--use-dont-care", action="store_true", help="do not ignore 'DontCare' labels.")
    args = parser.parse_args()
    if args.training_samples < 0 or args.training_samples > 1:
        print("Invalid argument {} for --training-samples. Expected a percentage value between 0.0 and 1.0.")
        exit(-1)
    return args

def main():
    args = parseArguments()

    if not os.path.exists(OUT_LABELS_DIR):
        os.makedirs(OUT_LABELS_DIR)

    print("Generating darknet labels...")
    sample_img_pathes = []
    for dir_path, sub_dirs, files in os.walk("./labels"):
        for file_name in files:
            if file_name.endswith(".txt"):
                lbl_path = os.path.join(dir_path, file_name)
                sample_id = getSampleId(lbl_path)
                img_path = os.path.join("./images", "{}.png".format(sample_id))
                sample_img_pathes.append(img_path)
                yolo_labels = parseSample(lbl_path, img_path)
                with open(os.path.join(OUT_LABELS_DIR, "{}.txt".format(sample_id)), "w") as yolo_label_file:
                    for lbl in yolo_labels:
                        yolo_label_file.write("{} {} {} {} {}\n".format(*lbl))

    # print("Writing training and test sample ids...")
    # first_test_sample_index = int(args.training_samples * len(sample_img_pathes))
    # with open("kitti_train.txt", "w") as train_file:
    #     for sample_index in range(first_test_sample_index):
    #         train_file.write("{}\n".format(sample_img_pathes[sample_index]))
    # with open("kitti_test.txt", "w") as test_file:
    #     for sample_index in range(first_test_sample_index, len(sample_img_pathes)):
    #         test_file.write("{}\n".format(sample_img_pathes[sample_index]))

if __name__ == "__main__":
    main()