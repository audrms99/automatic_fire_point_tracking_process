'''
main.py에서 사용하는 코드
'''

import socket
import json
import time
import os
from config import SERVER_CONFIG, DEBUG_CONFIG

class ServerConnection:
    def __init__(self, ip=None, port=None, password=None):
        self.SERVER_IP = ip or SERVER_CONFIG['host']
        self.SERVER_PORT = port or SERVER_CONFIG['port']
        self.PASSWORD = password or SERVER_CONFIG['password']
        self.client_socket = None
        self.detection_data = []
        self.reconnect_attempts = SERVER_CONFIG['reconnect_attempts']
        self.reconnect_delay = SERVER_CONFIG['reconnect_delay']

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.SERVER_IP, self.SERVER_PORT))
            
            auth_data = {
                'password': self.PASSWORD,
                'client_id': SERVER_CONFIG['client_id']
            }
            self.client_socket.send(json.dumps(auth_data).encode())
            
            response = self.client_socket.recv(1024).decode()
            if response != "AUTH_OK":
                raise Exception("인증 실패")
            print("서버에 연결되었습니다.")
            return True
            
        except Exception as e:
            print(f"서버 연결 실패: {e}")
            return False

    def reconnect(self):
        retry_count = 0
        
        while retry_count < self.reconnect_attempts:
            print(f"재연결 시도 {retry_count + 1}/{self.reconnect_attempts}")
            if self.connect():
                return True
            retry_count += 1
            time.sleep(self.reconnect_delay)
        return False

    def send_data(self, data):
        try:
            self.detection_data.append(data)
            
            if DEBUG_CONFIG['save_detections']:
                self.save_detection_data()
            
            self.client_socket.send(json.dumps(data).encode())
            return True
        except socket.error as e:
            print(f"데이터 전송 실패: {e}")
            return False

    def save_detection_data(self):
        try:
            save_dir = SERVER_CONFIG['log_directory']
            os.makedirs(save_dir, exist_ok=True)
            
            filename = f"{save_dir}/detection_fire_v1.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.detection_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"데이터 저장 실패: {e}")

    def close(self):
        if self.client_socket:
            self.client_socket.close()
