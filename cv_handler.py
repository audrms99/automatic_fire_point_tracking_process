'''
main.py에서 사용하는 코드
'''

import cv2
from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
import time
from sms_handler import SMSHandler
from config import SMS_CONFIG, CAMERA_CONFIG

class CameraHandler:
    def __init__(self, stream_url=None):
        self.stream_url = stream_url or CAMERA_CONFIG['stream_url']
        self.cap = None
        self.sms_handler = SMSHandler()
        self.last_sms_time = 0

    def connect(self):
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            print("Error: 비디오 스트림을 열 수 없습니다.")
            return False
        return True

    def read_frame(self):
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if not ret:
            print("Error: 프레임을 읽을 수 없습니다.")
        return ret, frame

    def draw_detection(self, frame, box, label):
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, label, (x, y + 30), 
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
        return frame

    def show_frame(self, frame):
        cv2.imshow("Image", frame)
        return cv2.waitKey(1) & 0xFF == ord('q')

    def release(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def process_detections(self, frame, yolo, angle_calculator, server):
        """프레임에서 객체를 감지하고 처리하는 메소드"""
        # 객체 감지
        boxes, class_ids, confidences, indexes = yolo.detect(frame)
        
        # 감지 데이터 초기화
        detection_data = None
        
        # 감지된 객체가 있을 때만 SMS 발송
        if len(indexes) > 0:
            current_time = time.time()
            if current_time - self.last_sms_time >= 60:  # 1분에 한 번만 발송
                if self.sms_handler.send_fire_alert():
                    self.last_sms_time = current_time  # SMS 발송 후 시간 업데이트
        
        # 감지된 객체 처리
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(yolo.classes[class_ids[i]])
                center_x = x + w//2
                center_y = y + h//2

                # 각도 계산
                pan_angle, tilt_angle = angle_calculator.find_nearest_angles(center_x, center_y)

                # 위치 임계값 확인 및 데이터 전송
                if angle_calculator.check_position_threshold(center_x, center_y):
                    detection_data = {
                        'pan_angle': int(pan_angle),
                        'tilt_angle': int(tilt_angle),
                        'label': label,
                        'confidence': float(confidences[i])
                    }
                    
                    # 서버로 데이터 전송
                    if not server.send_data(detection_data):
                        if not server.reconnect():
                            print("서버 재연결 실패")
                    
                    # 바운딩 박스 그리기
                    frame = self.draw_detection(frame, boxes[i], label)
        
        return frame, detection_data

class SMSHandler:
    def __init__(self):
        # API 키 설정
        self.api_key = SMS_CONFIG['api_key']
        self.api_secret = SMS_CONFIG['api_secret']
        self.cool = Message(self.api_key, self.api_secret)
        
        # 기본 SMS 설정
        self.default_params = {
            'type': 'sms',
            'from': SMS_CONFIG['from_number']
        }

    def send_fire_alert(self, to_number=None, custom_message=None):
        """화재 감지 시 SMS 발송"""
        try:
            params = self.default_params.copy()
            params['to'] = to_number or SMS_CONFIG['to_number']
            params['text'] = custom_message or SMS_CONFIG['default_message']

            response = self.cool.send(params)
            
            # 발송 결과 출력
            print("Success Count : %s" % response['success_count'])
            print("Error Count : %s" % response['error_count'])
            print("Group ID : %s" % response['group_id'])

            if "error_list" in response:
                print("Error List : %s" % response['error_list'])
                
            return response['success_count'] > 0

        except CoolsmsException as e:
            print("Error Code : %s" % e.code)
            print("Error Message : %s" % e.msg)
            return False
