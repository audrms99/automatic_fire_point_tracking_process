'''
main.py에서 사용하는 코드
'''

import numpy as np
from config import ANGLE_CONFIG, CAMERA_CONFIG

class AngleCalculator:
    def __init__(self):
        self.initial_x = None
        self.initial_y = None
        self.POSITION_THRESHOLD = ANGLE_CONFIG['position_threshold']
        
        self.PIXEL_WIDTH = CAMERA_CONFIG['frame_width']
        self.PIXEL_HEIGHT = CAMERA_CONFIG['frame_height']
        
        # 측정된 데이터를 저장할 배열 초기화 [x, y, pan_angle, tilt_angle]
        self.measured_data = np.array([
            [77,25,85,179],[148,25,90,170],[224,26,95,170],[281,29,100,170],[394,31,110,170],[338,27,105,170],
            [17,74,80,165],[72,72,85,165],[144,78,90,165],[219,75,95,165],[315,77,100,165],[394,75,105,165],[528,81,110,165],[469,77,115,165],
            [22,124,80,160],[85,124,85,160],[139,120,90,160],[218,122,95,160],[273,113,100,160],[350,115,105,160],[408,121,110,160],[470,123,115,160],
            [24,168,80,155],[86,155,85,155],[140,155,90,155],[216,157,95,155],[227,159,100,155],[348,162,105,155],[399,162,110,155],[470,160,120,155],
            [24,205,80,150],[74,205,85,150],[129,205,90,150],[191,207,95,150],[248,207,100,150],[312,209,105,150],[375,209,110,150],[435,209,115,150],[478,209,120,150],
            [21,245,80,145],[63,253,85,145],[122,253,90,145],[190,253,95,145],[247,253,100,145],[312,255,105,145],[372,254,110,145],[428,252,115,145],[479,250,120,145],
            [24,288,80,140],[84,288,85,140],[138,289,90,140],[190,289,95,140],[230,304,100,140],[312,299,105,140],[366,305,110,140],[416,306,115,140],[478,305,120,140],
            [17,350,80,135],[78,353,85,135],[140,351,90,135],[197,351,95,135],[244,353,100,135],[307,353,105,135],[361,355,110,135],[414,353,115,135],[477,354,120,135],
            [23,433,80,130],[70,418,85,130],[134,416,90,130],[190,413,95,130],[250,411,100,130],[355,415,110,130],[400,420,115,130],[456,419,120,130],
            [38,475,80,125],[89,477,85,125],[150,477,90,125],[200,477,95,125],[242,477,100,125],[299,467,105,125],[305,468,110,125],[391,467,115,125],[434,465,120,125],[474,470,125,125]
        ])

    def find_nearest_angles(self, detection_x, detection_y):
        """디텍션된 좌표에서 가장 가까운 측정점의 각도를 찾음"""
        if not (0 <= detection_x <= self.PIXEL_WIDTH and 0 <= detection_y <= self.PIXEL_HEIGHT):
            raise ValueError("디텍션 좌표가 유효한 범위를 벗어났습니다.")

        # 유클리드 거리 계산
        distances = np.sqrt(
            (self.measured_data[:, 0] - detection_x) ** 2 + 
            (self.measured_data[:, 1] - detection_y) ** 2
        )
        
        # 가장 가까운 점의 인덱스
        nearest_idx = np.argmin(distances)
        
        # 가장 가까운 점의 pan, tilt 각도
        nearest_point = self.measured_data[nearest_idx]
        pan_angle = nearest_point[2]
        tilt_angle = nearest_point[3]
        
        print(f"디텍션 좌표: ({detection_x}, {detection_y})")
        print(f"가장 가까운 측정점: ({nearest_point[0]}, {nearest_point[1]})")
        print(f"반환 각도 - Pan: {pan_angle}°, Tilt: {tilt_angle}°")
        
        return pan_angle, tilt_angle
    def check_position_threshold(self, current_x, current_y):
        """위치 변화량이 임계값을 초과하는지 확인"""
        if self.initial_x is None and self.initial_y is None:
            self.initial_x = current_x
            self.initial_y = current_y
            print(f"초기 위치 설정 - X: {current_x}, Y: {current_y}")
            return True

        x_diff = abs(current_x - self.initial_x)
        y_diff = abs(current_y - self.initial_y)

        if x_diff > self.POSITION_THRESHOLD or y_diff > self.POSITION_THRESHOLD:
            self.initial_x = current_x
            self.initial_y = current_y
            print(f"위치 변화량 - X: {x_diff}px, Y: {y_diff}px")
            return True

        return False

