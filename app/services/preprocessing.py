class HealthData(BaseModel):
    bpm_data: list  # [{"value": 72, "startDate": "2023-06-09T10:00:00Z", ...}, ...]

# 3. 피처 생성 함수
def extract_features(bpm_data, now=None):
    # DataFrame으로 변환
    df = pd.DataFrame(bpm_data)
    df['startDate'] = pd.to_datetime(df['startDate'])
    df = df.sort_values('startDate')

    now = now or pd.Timestamp.utcnow()
    window_sec = 60  # 최근 1분

    window = df[df['startDate'] >= now - timedelta(seconds=window_sec)]

    values = window['value'].astype(float).values
    if len(values) == 0:
        values = np.array([0.0])  # 최소값 대체

    # 통계 피처 계산
    features = {
        'bpm#AVG#60': float(np.mean(values)),
        'bpm#STD#60': float(np.std(values, ddof=1)),
        'bpm#MED#60': float(np.median(values)),
        'bpm#SKW#60': float(skew(values)) if len(values) > 2 else 0.0,
        'bpm#KUR#60': float(kurtosis(values)) if len(values) > 2 else 0.0,
        'bpm#ASC#60': float(np.sum(np.abs(np.diff(values)))) if len(values) > 1 else 0.0,
        'bpm#TSC#60': float(np.sqrt(np.sum(np.power(np.diff((values - np.mean(values)) / (np.std(values) + 1e-6)), 2))))
    }

    # 시간 기반 one-hot 피처 생성
    dt = now
    day = dt.strftime('%a').upper()[:3]  # e.g., 'MON'
    hour = dt.hour
    hour_name = (
        'DAWN' if 6 <= hour < 9 else
        'MORNING' if 9 <= hour < 12 else
        'AFTERNOON' if 12 <= hour < 15 else
        'LATE_AFTERNOON' if 15 <= hour < 18 else
        'EVENING' if 18 <= hour < 21 else
        'NIGHT' if 21 <= hour < 24 else 'MIDNIGHT'
    )
    is_weekend = dt.weekday() >= 5

    for d in ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']:
        features[f'ESM#DOW={d}'] = (d == day)

    for d in ['Y', 'N']:
        features[f'ESM#WKD={d}'] = (d == 'Y' if is_weekend else d == 'N')

    for h in ['DAWN', 'MORNING', 'AFTERNOON', 'LATE_AFTERNOON', 'EVENING', 'NIGHT', 'MIDNIGHT']:
        features[f'ESM#HRN={h}'] = (h == hour_name)

    return features