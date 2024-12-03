'''
SMS 발송을 위한 핸들러
main.py에서 사용하는 코드
'''

from sdk.api.message import Message
from sdk.exceptions import CoolsmsException
import time

class SMSHandler:
    def __init__(self, config):
        # API 키 설정
        self.api_key = config['api_key']
        self.api_secret = config['api_secret']
        self.cool = Message(self.api_key, self.api_secret)
        
        # 기본 SMS 설정
        self.default_params = {
            'type': 'sms',
            'from': config['from_number']  # 발신자 번호
        }
        
        # SMS 쿨다운 설정
        self.cooldown = config['sms_cooldown']
        self.last_sent = 0
        self.default_to_number = config['to_number']
        self.default_message = config['default_message']

    def send_fire_alert(self, to_number=None, custom_message=None):
        """화재 감지 시 SMS 발송"""
        # 쿨다운 체크
        current_time = time.time()
        if current_time - self.last_sent < self.cooldown:
            print(f"SMS 쿨다운 중입니다. {self.cooldown - (current_time - self.last_sent):.1f}초 후 재시도 가능")
            return False

        try:
            params = self.default_params.copy()
            params['to'] = to_number or self.default_to_number
            params['text'] = custom_message or self.default_message

            response = self.cool.send(params)
            
            # 발송 성공 시 마지막 발송 시간 업데이트
            if response['success_count'] > 0:
                self.last_sent = current_time
            
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