

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';

type Delivery = {
  id: number;
  address: string;
  status: string;
  customer: string;
  phone: string;
  
};

export default function ManifestScreen() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);

  useEffect(() => {
    // Load local JSON file
    import('@/assets/manifest.json')
      .then((data) => setDeliveries(data.default || data))
      .catch(() => setDeliveries([]));
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manifest</Text>
      <FlatList
        data={deliveries}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text style={styles.address}>Delivery #{item.id}: {item.address}</Text>
            <Text style={styles.status}>Status: {item.status}</Text>
            <Text style={styles.detail}>Customer: {item.customer}</Text>
            <Text style={styles.detail}>Phone: {item.phone}</Text>
          </View>
        )}
        ListEmptyComponent={<Text>No deliveries found.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
  },
  item: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  address: {
    fontSize: 18,
    fontWeight: '500',
  },
  status: {
    fontSize: 16,
    color: '#888',
    marginBottom: 4,
  },
  detail: {
    fontSize: 15,
    color: '#444',
    marginBottom: 2,
  },
});
