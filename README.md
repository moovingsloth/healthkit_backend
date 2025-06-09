# HealthKit Backend

건강 데이터를 기반으로 집중도를 예측하는 백엔드 API 서버입니다.

## 시스템 아키텍처

```mermaid
graph TD
    A[모바일 클라이언트] --> |HTTP/WebSocket 요청| B[FastAPI]
    B --> |데이터 저장/조회| C[(MongoDB)]
    B --> |캐싱| D[(Redis)]
    B --> |분석 데이터| E[ML 예측 모델]
    B --> |외부 연동| F[Google Sheets API]
    E --> |학습 데이터 저장| C
    
    subgraph "백엔드 서버"
        B
        E
    end
    
    subgraph "데이터 저장소"
        C
        D
    end
````

## 필수 요구사항

- Python 3.12
- MongoDB
- Redis

## 설치 방법

1. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate  # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
`.env` 파일을 프로젝트 루트에 생성하고 다음 변수들을 설정합니다:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=healthkit
REDIS_URL=redis://localhost:6379
```

## 실행 방법

1. MongoDB 실행:
```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB
```

2. Redis 실행:
```bash
# macOS (Homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Windows
redis-server
```

3. FastAPI 서버 실행:
```bash
uvicorn app.main:app --reload
```

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker로 실행

1. Docker Compose로 실행:
```bash
docker-compose up --build
```

2. 개별 컨테이너로 실행:
```bash
# MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Redis
docker run -d -p 6379:6379 --name redis redis:latest

# API 서버
docker build -t healthkit-backend .
docker run -d -p 8000:8000 --name api healthkit-backend
```

## API 엔드포인트

- `GET /`: API 상태 확인
- `GET /health`: 헬스 체크
- `POST /predict/concentration`: 집중도 예측
- `GET /api/user/{user_id}/profile`: 사용자 프로필 조회
- `GET /api/user/{user_id}/concentration-analysis`: 집중도 분석
- `GET /api/user/{user_id}/focus-pattern`: 집중도 패턴 조회
- `WS /ws/{user_id}`: WebSocket 연결 (실시간 데이터)

## 개발 환경 설정

1. 코드 포맷팅:
```bash
black .
```

2. 린트 검사:
```bash
flake8
```

3. 테스트 실행:
```bash
pytest
```

## 기능

- 건강 데이터 수집 및 저장
- 집중도 예측
- 사용자 프로필 관리
- 집중도 패턴 분석
- Google Sheets 연동
- Redis 캐싱
- MongoDB 데이터 저장

## 기술 스택

- FastAPI
- MongoDB
- Redis
- Google Sheets API
- Docker
- DigitalOcean

## 개발 환경 설정

1. 저장소 클론
```bash
git clone <repository-url>
cd HealthKit_Backend
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 추가
```

5. 로컬 개발 서버 실행
```bash
uvicorn app.main:app --reload
```

## Docker를 사용한 실행

1. Docker 이미지 빌드
```bash
docker-compose build
```

2. 서비스 실행
```bash
docker-compose up
```

## DigitalOcean 배포

1. DigitalOcean CLI 설치
```bash
brew install doctl  # Mac
```

2. DigitalOcean 인증
```bash
doctl auth init
```

3. 컨테이너 레지스트리 로그인
```bash
doctl registry login
```

4. 이미지 빌드 및 푸시
```bash
docker build -t registry.digitalocean.com/your-registry/healthkit-backend .
docker push registry.digitalocean.com/your-registry/healthkit-backend
```

5. DigitalOcean App Platform에서 배포
- DigitalOcean 대시보드에서 App Platform 선택
- GitHub 저장소 연결 또는 이미지 직접 배포
- 환경 변수 설정
- 배포 실행

## DigitalOcean App Platform 배포 가이드

### 사전 준비

1. [DigitalOcean 계정](https://www.digitalocean.com/) 생성
2. [GitHub 저장소](https://github.com/) 준비
3. [GitHub Actions](https://github.com/features/actions) 활성화

### 수동 배포 방법

1. DigitalOcean CLI 설치 및 인증
```bash
# doctl CLI 설치
brew install doctl  # Mac
# 또는
snap install doctl  # Ubuntu

# DigitalOcean 인증
doctl auth init
```

2. 컨테이너 레지스트리 로그인
```bash
doctl registry login
```

3. 이미지 빌드 및 푸시
```bash
docker build -t registry.digitalocean.com/healthkit/backend:latest .
docker push registry.digitalocean.com/healthkit/backend:latest
```

4. App Platform 앱 업데이트
```bash
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

### GitHub Actions 자동화 배포

GitHub Actions를 통해 배포를 자동화했습니다. `master` 브랜치에 변경사항이 푸시되면 자동으로 배포됩니다.

필요한 시크릿:
- `DIGITALOCEAN_ACCESS_TOKEN`: DigitalOcean API 토큰
- `DIGITALOCEAN_APP_ID`: DigitalOcean App Platform 앱 ID

GitHub 저장소 설정에서 이 시크릿을 설정하세요:
1. 저장소 페이지 → Settings → Secrets and variables → Actions
2. "New repository secret" 버튼 클릭
3. 각 시크릿 이름과 값 입력

### 배포 상태 확인

```bash
# 앱 상태 확인
doctl apps get YOUR_APP_ID
```

### 문제 해결

로그 확인:
```bash
doctl apps logs YOUR_APP_ID
```

배포 중에 문제가 발생하면 Docker 빌드나 환경 변수 설정을 확인하세요.

### 프론트엔드 연결

프론트엔드 앱에서 다음 URL을 사용하여 API에 연결할 수 있습니다:
```
https://your-app-name.ondigitalocean.app/
```

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| MONGODB_URL | MongoDB 연결 URL | mongodb://localhost:27017 |
| MONGODB_DB_NAME | MongoDB 데이터베이스 이름 | healthkit |
| REDIS_URL | Redis 연결 URL | redis://localhost:6379 |
| CACHE_TTL | 캐시 유효 시간(초) | 3600 |
| GOOGLE_SHEETS_CREDENTIALS_FILE | Google Sheets 인증 파일 경로 | credentials.json |
| GOOGLE_SHEETS_ID | Google Sheets ID | - |
| SECRET_KEY | JWT 시크릿 키 | - |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT 토큰 만료 시간(분) | 11520 |

## 라이선스

MIT