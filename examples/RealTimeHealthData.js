import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import wsClient from './websocket';
import { healthApi } from './api';

const RealTimeHealthData = ({ userId }) => {
  const [healthData, setHealthData] = useState(null);
  const [concentration, setConcentration] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // WebSocket 연결
    wsClient.connect();

    // 연결 상태 구독
    wsClient.subscribe('connection_status', (status) => {
      setIsConnected(status.connected);
    });

    // 건강 데이터 업데이트 구독
    wsClient.subscribe('health_data_update', (data) => {
      setHealthData(data);
    });

    // 집중도 업데이트 구독
    wsClient.subscribe('concentration_update', (data) => {
      setConcentration(data);
    });

    // 초기 데이터 로드
    loadInitialData();

    // 컴포넌트 언마운트 시 정리
    return () => {
      wsClient.disconnect();
    };
  }, [userId]);

  const loadInitialData = async () => {
    try {
      const [metrics, analysis] = await Promise.all([
        healthApi.getHealthMetrics(userId),
        healthApi.getFocusAnalysis(userId)
      ]);
      setHealthData(metrics);
      setConcentration(analysis);
    } catch (error) {
      console.error('초기 데이터 로드 중 오류:', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>
          연결 상태: {isConnected ? '연결됨' : '연결 끊김'}
        </Text>
      </View>

      {healthData && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>현재 건강 상태</Text>
          <View style={styles.dataRow}>
            <Text style={styles.label}>심박수:</Text>
            <Text style={styles.value}>{healthData.heart_rate} BPM</Text>
          </View>
          <View style={styles.dataRow}>
            <Text style={styles.label}>걸음 수:</Text>
            <Text style={styles.value}>{healthData.steps} 걸음</Text>
          </View>
          <View style={styles.dataRow}>
            <Text style={styles.label}>수면 시간:</Text>
            <Text style={styles.value}>{healthData.sleep_hours} 시간</Text>
          </View>
          <View style={styles.dataRow}>
            <Text style={styles.label}>스트레스 수준:</Text>
            <Text style={styles.value}>{healthData.stress_level}/5</Text>
          </View>
        </View>
      )}

      {concentration && (
        <View style={styles.dataContainer}>
          <Text style={styles.sectionTitle}>집중도 분석</Text>
          <View style={styles.dataRow}>
            <Text style={styles.label}>현재 집중도:</Text>
            <Text style={styles.value}>{concentration.current_level}%</Text>
          </View>
          <View style={styles.dataRow}>
            <Text style={styles.label}>일일 평균:</Text>
            <Text style={styles.value}>{concentration.daily_average}%</Text>
          </View>
          <View style={styles.dataRow}>
            <Text style={styles.label}>최고 집중 시간:</Text>
            <Text style={styles.value}>{concentration.peak_hours.join(', ')}시</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  statusContainer: {
    padding: 10,
    backgroundColor: '#f5f5f5',
    marginBottom: 10,
  },
  statusText: {
    textAlign: 'center',
    color: '#666',
  },
  dataContainer: {
    padding: 15,
    backgroundColor: '#fff',
    borderRadius: 10,
    margin: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 16,
    color: '#666',
  },
  value: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
});

export default RealTimeHealthData; 