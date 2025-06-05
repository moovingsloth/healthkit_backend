// 환경별 API URL 설정
const ENV = {
  dev: {
    API_URL: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000',
  },
  staging: {
    API_URL: 'https://staging-api.yourdomain.com',
    WS_URL: 'wss://staging-api.yourdomain.com',
  },
  prod: {
    API_URL: 'https://api.yourdomain.com',
    WS_URL: 'wss://api.yourdomain.com',
  },
};

// 현재 환경 설정 (개발 환경으로 기본 설정)
const getEnvVars = (env = 'dev') => {
  return ENV[env];
};

export default getEnvVars; 