import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function DeliveryUpdatesScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Delivery Updates</Text>
      <Text>This is the Delivery Updates screen.</Text>
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
