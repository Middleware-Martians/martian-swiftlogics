import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function ProofOfDeliveryScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Proof of Delivery</Text>
      <Text>This is the Proof of Delivery screen.</Text>
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
