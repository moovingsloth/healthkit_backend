import numpy as np
import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 더 정확한 모델 학습을 위한 스크립트
def create_improved_model():
    # 샘플 데이터 생성 (실제로는 좀 더 많은 데이터가 필요)
    np.random.seed(42)
    n_samples = 500
    
    # 특성 생성
    heart_rates = np.random.normal(70, 10, n_samples)  # 평균 70, 표준편차 10의 심박수
    steps = np.random.normal(5000, 2000, n_samples)    # 평균 5000, 표준편차 2000의 걸음 수
    sleep_hours = np.random.normal(7, 1.5, n_samples)  # 평균 7시간, 표준편차 1.5시간의 수면
    stress_levels = np.random.normal(5, 2, n_samples)  # 평균 5, 표준편차 2의 스트레스 레벨
    
    # 복잡한 규칙으로 집중도 라벨 생성 (0: 낮음, 1: 중간, 2: 높음)
    concentration = []
    for hr, step, sleep, stress in zip(heart_rates, steps, sleep_hours, stress_levels):
        if sleep < 5 or stress > 8:  # 수면 부족하거나 스트레스 높으면
            c = 0  # 낮은 집중도
        elif 60 < hr < 75 and sleep > 7 and stress < 5:  # 적절한 심박수, 충분한 수면, 낮은 스트레스
            c = 2  # 높은 집중도
        else:
            c = 1  # 중간 집중도
        concentration.append(c)
    
    # 데이터프레임 생성
    data = pd.DataFrame({
        'heart_rate': heart_rates,
        'step_count': steps,
        'sleep_hours': sleep_hours,
        'stress_level': stress_levels,
        'concentration': concentration
    })
    
    # 모델 학습용 데이터 분할
    X = data[['heart_rate', 'step_count', 'sleep_hours', 'stress_level']]
    y = data['concentration']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # RandomForest 모델 학습
    model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10,
        min_samples_split=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 모델 평가
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    print(f"모델 학습 정확도: {train_score:.4f}")
    print(f"모델 테스트 정확도: {test_score:.4f}")
    
    # 모델 저장
    os.makedirs('model', exist_ok=True)
    with open('model/concentration_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print(f"모델이 'model/concentration_model.pkl'에 저장되었습니다.")
    
    # 테스트 예측
    test_data = [
        [70, 6000, 7, 3],  # 양호한 건강 데이터 (높은 집중도 예상)
        [90, 2000, 4, 9],  # 좋지 않은 건강 데이터 (낮은 집중도 예상)
        [75, 5000, 6, 5]   # 보통 건강 데이터 (중간 집중도 예상)
    ]
    predictions = model.predict_proba(test_data)
    print("\n테스트 예측 결과:")
    for i, pred in enumerate(predictions):
        print(f"데이터 {i+1}: 클래스별 확률 {pred}")
    
if __name__ == "__main__":
    create_improved_model()