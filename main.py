'''
server에서 돌려야하는 코드

'''

from yolov3_detector import YOLODetector
from server_connection import ServerConnection
from cal_angle import AngleCalculator
from cv_handler import CameraHandler
from data_handler import DetectionDataHandler
from config import SERVER_CONFIG, DEBUG_CONFIG

def main():
    # YOLO 설정
    yolo = YOLODetector()

    # 서버 연결 설정
    server = ServerConnection(
        ip=SERVER_CONFIG['host'],
        port=SERVER_CONFIG['port'],
        password=SERVER_CONFIG['password']
    )
    if not server.connect():
        return

    # 각도 계산기 초기화
    angle_calculator = AngleCalculator()

    # 카메라 설정
    camera = CameraHandler()
    if not camera.connect():
        return

    # 데이터 핸들러 초기화
    data_handler = DetectionDataHandler()

    try:
        while True:
            ret, frame = camera.read_frame()
            if not ret:
                break

            # 객체 감지 및 처리
            frame, detection_data = camera.process_detections(frame, yolo, angle_calculator, server)
            
            # JSON 파일로 저장
            if detection_data and DEBUG_CONFIG['save_detections']:
                data_handler.save_detection_data(detection_data)

            # 결과 화면 출력
            if DEBUG_CONFIG['show_frames']:
                if camera.show_frame(frame):
                    break

    finally:
        server.close()
        camera.release()

if __name__ == "__main__":
    main()