'''
raps#2(sensor) server
'''

import socket
import json
from motor_control import MotorController
from data_handler import DetectionDataHandler
from queue import Queue
import time
import math

class FireDetectionServer:
    def __init__(self):
        # TCP 서버 설정
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 8485
        self.BUFFER_SIZE = 1024
        self.PASSWORD = "your_secure_password"

        # 모터 컨트롤러 초기화
        self.motor_controller = MotorController()
        
        # 데이터 핸들러 초기화
        self.data_handler = DetectionDataHandler()

        # 소켓 초기화
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.TCP_IP, self.TCP_PORT))
        self.server_socket.listen(1)

        self.data_queue = Queue()
        self.is_processing = False

    def authenticate_client(self, conn):
        try:
            data = conn.recv(self.BUFFER_SIZE)
            auth_data = json.loads(data.decode())
            if auth_data.get('password') == self.PASSWORD:
                conn.send("AUTH_OK".encode())
                return True
            conn.send("AUTH_FAILED".encode())
            return False
        except:
            return False

    def process_received_data(self, data):
        """수신된 데이터를 큐에 추가하고 처리 시작"""
        try:
            received_data = json.loads(data.decode())
            self.data_queue.put(received_data)
            
            # 현재 처리 중이 아닐 때만 새로운 처리 시작
            if not self.is_processing:
                self.process_queue()
                
        except json.JSONDecodeError as e:
            print(f"데이터 파싱 오류: {e}")
        except Exception as e:
            print(f"처리 중 오류 발생: {e}")

    def process_queue(self):
        """큐에 있는 데이터를 순차적으로 처리"""
        if self.is_processing:
            return
            
        self.is_processing = True
        
        try:
            while not self.data_queue.empty():
                try:
                    data = self.data_queue.get()
                    
                    # pan과 tilt 각도 모두 확인
                    if not isinstance(data, dict) or ('pan_angle' not in data and 'tilt_angle' not in data):
                        print("잘못된 데이터 형식입니다")
                        print(f"수신된 데이터: {data}")  # 디버깅을 위해 추가
                        continue
                    
                    pan_angle = data.get('pan_angle')
                    tilt_angle = data.get('tilt_angle')
                    
                    # 각도 값 유효성 검사 추가
                    if not isinstance(pan_angle, (int, float)) or not (0 <= pan_angle <= 360):
                        print(f"유효하지 않은 pan 각도 값입니다: {pan_angle}")
                        continue
                    
                    if not isinstance(tilt_angle, (int, float)) or not (0 <= tilt_angle <= 360):
                        print(f"유효하지 않은 tilt 각도 값입니다: {tilt_angle}")
                        continue
                    
                    print(f"수신된 각도: pan_angle={pan_angle}, tilt_angle={tilt_angle}")
                    
                    # 모터 제어 시도
                    try:
                        self.motor_controller.process_angle(pan_angle, tilt_angle)
                    except Exception as motor_error:
                        print(f"모터 제어 중 오류 발생: {motor_error}")
                        continue
                    
                    # 데이터 저장 시도
                    try:
                        detection_data = {
                            'pan_angle': pan_angle,
                            'tilt_angle': tilt_angle,
                            'source': 'fire_detection_server',
                            'timestamp': time.time()
                        }
                        self.data_handler.save_detection_data(detection_data)
                    except Exception as save_error:
                        print(f"데이터 저장 중 오류 발생: {save_error}")
                    
                    time.sleep(0.3)
                    
                except Exception as item_error:
                    print(f"개별 데이터 처리 중 오류 발생: {item_error}")
                    continue
                    
        except Exception as e:
            print(f"큐 처리 중 심각한 오류 발생: {e}")
        finally:
            self.is_processing = False

    def start(self):
        print(f"서버가 {self.TCP_PORT} 포트에서 시작되었습니다.")
        self.motor_controller.turn_off_all_pins()
        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"클라이언트 연결 시도: {addr}")
                
                if not self.authenticate_client(conn):
                    print("인증 실패")
                    conn.close()
                    continue
                    
                print(f"클라이언트 인증 성공: {addr}")
                
                while True:
                    data = conn.recv(self.BUFFER_SIZE)
                    if not data:
                        break
                    
                    self.process_received_data(data)

        except KeyboardInterrupt:
            print("서버를 종료합니다.")
        finally:
            if 'conn' in locals():
                conn.close()
            self.server_socket.close()
            self.motor_controller.cleanup()
            print("모든 리소스가 정리되었습니다.")

if __name__ == "__main__":
    server = FireDetectionServer()
    server.start()
