

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';

type Delivery = {
  id: number;
  address: string;
  status: string;
  customer: string;
  phone: string;
  deliveryTime?: string;
  items?: string[];
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
      <Text style={styles.title}>Delivery Manifest</Text>
      <FlatList
        data={deliveries}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.address}>#{item.id} - {item.address}</Text>
            <View style={styles.row}><Text style={styles.label}>Status:</Text><Text style={styles.status}>{item.status}</Text></View>
            <View style={styles.row}><Text style={styles.label}>Customer:</Text><Text style={styles.detail}>{item.customer}</Text></View>
            <View style={styles.row}><Text style={styles.label}>Phone:</Text><Text style={styles.detail}>{item.phone}</Text></View>
            {item.deliveryTime && (
              <View style={styles.row}><Text style={styles.label}>Delivery Time:</Text><Text style={styles.detail}>{item.deliveryTime}</Text></View>
            )}
            {item.items && (
              <View style={styles.row}><Text style={styles.label}>Items:</Text><Text style={styles.detail}>{item.items.join(', ')}</Text></View>
            )}
          </View>
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        ListEmptyComponent={<Text style={styles.empty}>No deliveries found.</Text>}
        contentContainerStyle={{ paddingBottom: 24 }}
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
    fontSize: 32,
    fontWeight: '900',
    marginTop: 32,
    marginBottom: 24,
    textAlign: 'center',
    color: '#00BDD6',
    fontFamily: 'System',
    letterSpacing: 1,
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
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 8,
    color: '#222',
    fontFamily: 'System',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  label: {
    fontWeight: 'bold',
    color: '#00BDD6',
    fontSize: 15,
    marginRight: 6,
    fontFamily: 'System',
  },
  status: {
    fontSize: 16,
    color: '#888',
    fontWeight: '500',
    fontFamily: 'System',
  },
  detail: {
    fontSize: 15,
    color: '#444',
    fontFamily: 'System',
  },
  separator: {
    height: 12,
    backgroundColor: '#f2f2f2',
    borderRadius: 8,
    marginHorizontal: 8,
  },
  empty: {
    textAlign: 'center',
    color: '#888',
    fontSize: 16,
    marginTop: 32,
    fontFamily: 'System',
  },
});
