'''
main.py에서 사용하는 코드
'''

import json
import os
from datetime import datetime

class DetectionDataHandler:
    def __init__(self, base_dir="detection_logs"):
        self.base_dir = base_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """저장 디렉토리가 존재하는지 확인하고 없으면 생성"""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def save_detection_data(self, detection_data, filename="detection_fire_v1.json"):
        """감지 데이터를 JSON 파일로 저장"""
        filepath = os.path.join(self.base_dir, filename)
        
        # 기존 데이터 읽기
        existing_data = []
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 타임스탬프 추가
        detection_data['timestamp'] = datetime.now().isoformat()
        
        # 새 데이터 추가
        existing_data.append(detection_data)
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
