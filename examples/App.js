import React from 'react';
import { SafeAreaView, StatusBar } from 'react-native';
import ConcentrationDashboard from './ConcentrationDashboard';

const App = () => {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <StatusBar barStyle="dark-content" />
      <ConcentrationDashboard userId="user123" />
    </SafeAreaView>
  );
};

export default App; 