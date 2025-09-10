import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function RouteScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Route</Text>
      <Text>This is the Route screen.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
});
