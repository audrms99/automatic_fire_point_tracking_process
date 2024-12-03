'''
main.py에서 사용하는 코드
'''

import cv2
import numpy as np
from config import YOLO_CONFIG

class YOLODetector:
    @staticmethod
    def get_default_paths():
        return YOLO_CONFIG

    def __init__(self, weights_path=None, cfg_path=None, names_path=None):
        paths = self.get_default_paths()
        self.weights_path = weights_path or paths['weights']
        self.cfg_path = cfg_path or paths['config']
        self.names_path = names_path or paths['names']
        # YOLO 모델 로드
        self.net = cv2.dnn.readNet(self.weights_path, self.cfg_path)
        
        # 클래스 이름 로드
        self.classes = []
        with open(self.names_path, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
            
        # 레이어 설정
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def detect(self, frame):
        height, width, _ = frame.shape

        # YOLO 입력을 위한 이미지 전처리
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        # 감지된 객체 정보
        class_ids = []
        confidences = []
        boxes = []

        # 감지 정보 추출
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # 객체 좌표 계산
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # 박스 좌표 계산
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Non-maximum suppression 적용
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        return boxes, class_ids, confidences, indexes
