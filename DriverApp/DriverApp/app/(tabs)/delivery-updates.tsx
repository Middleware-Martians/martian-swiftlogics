
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from 'react-native';

type Delivery = {
  id: number;
  address: string;
  status: string;
  customer: string;
  phone: string;
  deliveryTime?: string;
  items?: string[];
};

export default function DeliveryUpdatesScreen() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await import('@/assets/manifest.json');
        const all: Delivery[] = data.default || data;
        setDeliveries(all.filter(d => d.status === 'ongoing'));
      } catch {
        setDeliveries([]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const markAsDelivered = (id: number) => {
    setDeliveries(prev => prev.map(d => d.id === id ? { ...d, status: 'pending_customer_confirmation' } : d));
    Alert.alert('Delivery Updated', 'Customer has to confirm delivery.');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Delivery Updates</Text>
      {loading ? (
        <Text>Loading...</Text>
      ) : (
        <FlatList
          data={deliveries}
          keyExtractor={item => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.address}>{item.address}</Text>
              <Text style={styles.detail}>Customer: {item.customer}</Text>
              <Text style={styles.detail}>Phone: {item.phone}</Text>
              <TouchableOpacity
                style={[styles.button, item.status !== 'ongoing' && { backgroundColor: '#ccc' }]}
                onPress={() => markAsDelivered(item.id)}
                disabled={item.status !== 'ongoing'}
              >
                <Text style={styles.buttonText}>
                  {item.status === 'pending_customer_confirmation' ? 'Waiting for Customer Confirmation' : 'Mark as Delivered'}
                </Text>
              </TouchableOpacity>
            </View>
          )}
          ListEmptyComponent={<Text style={styles.empty}>No ongoing deliveries.</Text>}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#00BDD6',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 18,
    shadowColor: '#00BDD6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6,
    marginVertical: 6,
    marginHorizontal: 2,
  },
  address: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
    color: '#222',
  },
  detail: {
    fontSize: 15,
    color: '#444',
    marginBottom: 2,
  },
  button: {
    marginTop: 12,
    backgroundColor: '#00BDD6',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  empty: {
    textAlign: 'center',
    color: '#888',
    fontSize: 16,
    marginTop: 32,
  },
});
