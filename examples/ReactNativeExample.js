import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Alert } from 'react-native';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';  // 개발 환경
// const API_BASE_URL = 'https://api.yourdomain.com';  // 프로덕션 환경

const HealthKitExample = () => {
  const [healthData, setHealthData] = useState(null);
  const [prediction, setPrediction] = useState(null);

  // 건강 데이터 전송 함수
  const sendHealthData = async (data) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, {
        heart_rate: data.heartRate,
        steps: data.steps,
        sleep_hours: data.sleepHours,
        stress_level: data.stressLevel,
        timestamp: new Date().toISOString()
      });

      if (response.data.success) {
        setPrediction(response.data.data);
        return response.data;
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      Alert.alert('Error', error.message);
      throw error;
    }
  };

  // 사용자 프로필 조회 함수
  const getUserProfile = async (userId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${userId}/profile`);
      return response.data;
    } catch (error) {
      Alert.alert('Error', error.message);
      throw error;
    }
  };

  // 건강 지표 조회 함수
  const getHealthMetrics = async (userId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${userId}/metrics`);
      return response.data;
    } catch (error) {
      Alert.alert('Error', error.message);
      throw error;
    }
  };

  // 집중도 분석 조회 함수
  const getFocusAnalysis = async (userId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${userId}/focus-analysis`);
      return response.data;
    } catch (error) {
      Alert.alert('Error', error.message);
      throw error;
    }
  };

  // 예시 사용법
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 건강 데이터 전송 예시
        const healthData = {
          heartRate: 75,
          steps: 8000,
          sleepHours: 7.5,
          stressLevel: 3
        };
        await sendHealthData(healthData);

        // 사용자 프로필 조회 예시
        const profile = await getUserProfile('user123');
        console.log('User Profile:', profile);

        // 건강 지표 조회 예시
        const metrics = await getHealthMetrics('user123');
        console.log('Health Metrics:', metrics);

        // 집중도 분석 조회 예시
        const analysis = await getFocusAnalysis('user123');
        console.log('Focus Analysis:', analysis);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>HealthKit API Example</Text>
      {prediction && (
        <View style={styles.predictionContainer}>
          <Text style={styles.predictionTitle}>Concentration Prediction:</Text>
          <Text style={styles.predictionText}>
            Level: {prediction.concentration_level}
          </Text>
          <Text style={styles.predictionText}>
            Confidence: {prediction.confidence}%
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  predictionContainer: {
    padding: 15,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    marginTop: 20,
  },
  predictionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  predictionText: {
    fontSize: 16,
    marginBottom: 5,
  },
});

export default HealthKitExample; 