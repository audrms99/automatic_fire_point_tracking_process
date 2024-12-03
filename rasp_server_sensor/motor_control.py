'''
rasp#2(sensor) server에서 사용하는 코드
'''

import pigpio
import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        # GPIO 핀 설정
        self.PAN_PIN = 17 #팬 핀
        self.TILT_PIN = 18 #틸트 핀
        self.RELAY_PIN = 22 #팬틸트펌프 핀
        self.PUMP_RELAY_PIN = 12 #물펌프 핀
        self.LIGHT_RELAY_PIN = 21 #경광등 핀

        # pigpio 초기화
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise Exception("Pigpio 연결 실패. 데몬이 실행 중인지 확인하세요.")

        # GPIO 초기화
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        GPIO.setup(self.PUMP_RELAY_PIN, GPIO.OUT)
        GPIO.setup(self.LIGHT_RELAY_PIN, GPIO.OUT)
        
        # 초기화 시 모든 핀 OFF
        #self.turn_off_all_pins()

    def turn_off_all_pins(self):
        """모든 릴레이 핀을 OFF 상태로 설정"""
        pins = [self.RELAY_PIN, self.PUMP_RELAY_PIN, self.LIGHT_RELAY_PIN]
        for pin in pins:
            self.set_relay_state(pin, 'OFF')
        print("모든 릴레이 핀이 OFF 상태로 설정되었습니다.")

    def set_angle(self, pin, angle):
        if 0 <= angle <= 180:
            pulse = int(500 + (angle / 180.0) * 2000)
            self.pi.set_servo_pulsewidth(pin, pulse)
            print(f"{pin}번 핀에 {angle}°로 이동")

    def set_relay_state(self, pin, state):
        if state == 'ON':
            GPIO.output(pin, GPIO.LOW)
            print(f"릴레이 {pin} ON")
        elif state == 'OFF':
            GPIO.output(pin, GPIO.HIGH)
            print(f"릴레이 {pin} OFF")

    def run_pump(self):
        self.set_relay_state(self.PUMP_RELAY_PIN, 'ON')
        time.sleep(3)
        self.set_relay_state(self.PUMP_RELAY_PIN, 'OFF')
        print("펌프 작동 완료")

    def process_angle(self, pan_angle, tilt_angle):
        """pan_angle과 tilt_angle을 받아서 모터를 제어하는 메소드"""
        try:
            # 1. 경광등 작동
            self.set_relay_state(self.LIGHT_RELAY_PIN, 'ON')
            time.sleep(1)
            print(f"경광등 작동 완료")
            
            # 2. 모터 전원 공급
            self.set_relay_state(self.RELAY_PIN, 'ON')
            
            # 3. 팬 및 틸트 이동
            self.set_angle(self.PAN_PIN, pan_angle)
            time.sleep(1)
            self.set_angle(self.TILT_PIN, tilt_angle)
            time.sleep(1)
            print(f"팬 및 틸트 이동 완료 (pan: {pan_angle}°, tilt: {tilt_angle}°)") 
            
            # 4. 모터 전원 차단
            self.set_relay_state(self.RELAY_PIN, 'OFF')
            
            # 5. 펌프 작동
            self.run_pump()
            
            # 6. 경광등 종료
            self.set_relay_state(self.LIGHT_RELAY_PIN, 'OFF')
            
            # 7. 모터 대기 상태 유지
            self.set_relay_state(self.RELAY_PIN, 'ON')
            
        except Exception as e:
            print(f"모터 제어 중 오류 발생: {e}")
            raise

    def cleanup(self):
        """종료 시에도 모든 핀을 OFF로 설정"""
        self.turn_off_all_pins()
        self.pi.set_servo_pulsewidth(self.PAN_PIN, 0)
        self.pi.set_servo_pulsewidth(self.TILT_PIN, 0)
        self.pi.stop()
        GPIO.cleanup()
        print("모터 컨트롤러 정리 완료")
