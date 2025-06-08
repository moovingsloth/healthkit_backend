import os
import sys
import json
from datetime import datetime

# 상위 디렉토리를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.model import ConcentrationModel, get_concentration_prediction

def main():
    print("ConcentrationModel 테스트 시작")
    
    # 테스트용 건강 데이터 생성
    test_data = [
        {
            'date': '2025-06-01',
            'hour': 9,
            'heart_rate': 75,
            'step_count': 1200,
            'sleep_hours': 7,
            'stress_level': 3,
            'concentration_score': 0.7
        },
        {
            'date': '2025-06-01',
            'hour': 14,
            'heart_rate': 85,
            'step_count': 4500,
            'sleep_hours': 7,
            'stress_level': 5,
            'concentration_score': 0.6
        },
        {
            'date': '2025-06-02',
            'hour': 10,
            'heart_rate': 70,
            'step_count': 2000,
            'sleep_hours': 5,  # 수면 부족
            'stress_level': 8,  # 높은 스트레스
            'concentration_score': 0.4
        }
    ]
    
    # 모델 인스턴스 생성
    model = ConcentrationModel()
    
    # 1. 집중도 예측 테스트
    print("\n1. 집중도 예측 테스트:")
    predictions = model.predict_concentration(test_data)
    for i, pred in enumerate(predictions):
        print(f"  데이터 {i+1}: 예측 집중도 = {pred:.4f}")
    
    # 2. 패턴 분석 테스트
    print("\n2. 집중 패턴 분석 테스트:")
    analysis = model.analyze_focus_pattern(test_data)
    print(f"  일일 평균 집중도: {analysis['daily_average']:.4f}")
    print(f"  주간 트렌드: {analysis['weekly_trend']}")
    print(f"  최적 집중 시간대: {analysis['peak_hours']}")
    print(f"  개선 필요 날짜: {analysis['improvement_areas']}")
    print(f"  추천사항:")
    for rec in analysis['recommendations']:
        print(f"    - {rec}")
    
    # 3. 전역 함수 테스트
    print("\n3. 전역 함수 테스트:")
    global_predictions = get_concentration_prediction(test_data)
    print(f"  결과 길이: {len(global_predictions)}")
    print(f"  첫 번째 예측: {global_predictions[0]:.4f}")
    
    print("\n테스트 완료")

if __name__ == "__main__":
    main()