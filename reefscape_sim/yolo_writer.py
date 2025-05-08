import time
import asyncio
import json
import io

import omni.kit
import omni.usd
import omni.replicator.core as rep

from os import listdir
from os.path import isfile, join

from omni.replicator.core import Writer, AnnotatorRegistry, BackendDispatch

class YoloWriter(Writer):
    def __init__(
        self,
        output_dir,
        image_output_format="png",
        image_size=512
    ):
        self._output_dir = output_dir
        self._backend = BackendDispatch({"paths": {"out_dir": output_dir}})
        self._frame_id = 0
        self._image_output_format = image_output_format
        self._current_image_count = len([f for f in listdir(output_dir + "\\images") if isfile(join(output_dir, f))])
        self.image_size=image_size

        self.annotators = []

        # RGB
        self.annotators.append(AnnotatorRegistry.get_annotator("rgb"))

        # Bounding Box 2D
        self.annotators.append(AnnotatorRegistry.get_annotator("bounding_box_2d_tight",
                                                            init_params={"semanticTypes": ["class"]}))

    # def check_bbox_area(self, bbox_data, size_limit):
    #     length = abs(bbox_data['x_min'] - bbox_data['x_max'])
    #     width = abs(bbox_data['y_min'] - bbox_data['y_max'])

    #     area = length * width
    #     if area > size_limit:
    #         return True
    #     else:
    #         return False

    def write(self, data):
        write_items_buffer = io.BytesIO()

        image_id = self._current_image_count + self._frame_id
        yolo_image_filepath = f"images\\{image_id}.{self._image_output_format}"
        yolo_label_filepath = f"labels\\{image_id}.txt"

        if "rgb" in data and "bounding_box_2d_tight" in data:

            bbox_data = data["bounding_box_2d_tight"]["data"]
            id_to_labels = data["bounding_box_2d_tight"]["info"]["idToLabels"]

            for id, labels in id_to_labels.items():
                # print(id) print(labels['class'])
                id = int(id)

                # target_bbox_data = {'x_min': bbox_data['x_min'], 'y_min': bbox_data['y_min'],
                                    # 'x_max': bbox_data['x_max'], 'y_max': bbox_data['y_max']}

                # if self.check_bbox_area(target_bbox_data, 0.5):
                semantic_id = id

                x_center = (bbox_data['x_min'][0] + bbox_data['x_max'][0] / 2) / self.image_size
                y_center = (bbox_data['y_min'][0] + bbox_data['y_max'][0] / 2) / self.image_size

                width = int(abs(bbox_data['x_min'][0] - bbox_data['x_max'][0])) / self.image_size
                height = int(abs(bbox_data['y_min'][0] - bbox_data['y_max'][0])) / self.image_size

                write_items_buffer.write(f"{int(semantic_id)} {x_center} {y_center} {width} {height}\n".encode())
                print(f"{int(semantic_id)} {x_center} {y_center} {width} {height}\n")
        self._backend.write_image(yolo_image_filepath, data["rgb"])
        self._backend.write_blob(yolo_label_filepath, write_items_buffer.getvalue())

        self._frame_id += 1