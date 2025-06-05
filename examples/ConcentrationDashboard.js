import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { healthApi } from './api';
import WebSocketClient from './websocket';

const ConcentrationDashboard = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [concentrationData, setConcentrationData] = useState({
    daily_average: 0,
    weekly_trend: [],
    peak_hours: [],
    improvement_areas: []
  });
  const [healthMetrics, setHealthMetrics] = useState({
    heart_rate: 0,
    steps: 0,
    sleep_hours: 0,
    stress_level: 0
  });

  useEffect(() => {
    const ws = new WebSocketClient(userId);
    
    // WebSocket 이벤트 리스너 설정
    ws.addListener('health_update', (data) => {
      setHealthMetrics(prev => ({ ...prev, ...data.data }));
    });

    ws.addListener('concentration_update', (data) => {
      // 집중도 데이터 업데이트
      setConcentrationData(prev => ({
        ...prev,
        daily_average: data.data.concentration_score
      }));
    });

    // WebSocket 연결
    ws.connect();

    // 초기 데이터 로드
    loadData();

    return () => {
      ws.disconnect();
    };
  }, [userId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const analysis = await healthApi.getConcentrationAnalysis(userId);
      setConcentrationData(analysis);
      setError(null);
    } catch (err) {
      setError('데이터 로드 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>현재 집중도</Text>
        <Text style={styles.concentrationScore}>
          {concentrationData.daily_average.toFixed(1)}%
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>주간 트렌드</Text>
        <LineChart
          data={{
            labels: ['월', '화', '수', '목', '금', '토', '일'],
            datasets: [{
              data: concentrationData.weekly_trend
            }]
          }}
          width={350}
          height={200}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#ffffff',
            backgroundGradientTo: '#ffffff',
            decimalPlaces: 1,
            color: (opacity = 1) => `rgba(0, 122, 255, ${opacity})`,
            style: {
              borderRadius: 16
            }
          }}
          style={styles.chart}
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>건강 지표</Text>
        <View style={styles.metricsContainer}>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>심박수</Text>
            <Text style={styles.metricValue}>{healthMetrics.heart_rate} BPM</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>걸음 수</Text>
            <Text style={styles.metricValue}>{healthMetrics.steps}</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>수면 시간</Text>
            <Text style={styles.metricValue}>{healthMetrics.sleep_hours}시간</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>스트레스</Text>
            <Text style={styles.metricValue}>{healthMetrics.stress_level}/10</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>개선 영역</Text>
        {concentrationData.improvement_areas.map((area, index) => (
          <Text key={index} style={styles.improvementItem}>
            • {area}
          </Text>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: 'red',
    fontSize: 16,
    textAlign: 'center',
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  concentrationScore: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
    textAlign: 'center',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricItem: {
    width: '48%',
    backgroundColor: '#f8f8f8',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  improvementItem: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
});

export default ConcentrationDashboard; 