import axios from 'axios';
import getEnvVars from './env';

const env = getEnvVars();
const API_BASE_URL = env.API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 토큰이 있는 경우 헤더에 추가
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 처리
      localStorage.removeItem('token');
      // 로그인 페이지로 리다이렉트
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API 메서드
export const healthApi = {
  // 건강 데이터 저장
  storeHealthMetrics: async (metrics) => {
    try {
      const response = await api.post('/api/health-metrics', metrics);
      return response.data;
    } catch (error) {
      console.error('건강 데이터 저장 실패:', error);
      throw error;
    }
  },

  // 집중도 예측
  predictConcentration: async (metrics) => {
    try {
      const response = await api.post('/predict/concentration', metrics);
      return response.data;
    } catch (error) {
      console.error('집중도 예측 실패:', error);
      throw error;
    }
  },

  // 사용자 프로필 조회
  getUserProfile: async (userId) => {
    try {
      const response = await api.get(`/api/user/${userId}/profile`);
      return response.data;
    } catch (error) {
      console.error('사용자 프로필 조회 실패:', error);
      throw error;
    }
  },

  // 집중도 분석 조회
  getConcentrationAnalysis: async (userId) => {
    try {
      const response = await api.get(`/api/user/${userId}/concentration-analysis`);
      return response.data;
    } catch (error) {
      console.error('집중도 분석 조회 실패:', error);
      throw error;
    }
  },

  // 건강 지표 조회
  getHealthMetrics: async (userId) => {
    const response = await api.get(`/api/health-metrics/${userId}`);
    return response.data;
  },

  // 집중도 패턴 조회
  getFocusPattern: async (userId, startDate, endDate) => {
    const response = await api.get(`/api/user/${userId}/focus-pattern`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  },
};

export default api; 