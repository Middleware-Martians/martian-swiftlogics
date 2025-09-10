

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Dimensions, ActivityIndicator, Alert } from 'react-native';
import MapView, { Marker, Polyline, UrlTile } from 'react-native-maps';

type Delivery = {
  id: number;
  address: string;
  status: string;
  customer: string;
  phone: string;
  deliveryTime?: string;
  items?: string[];
};

// Geocode address using Nominatim API with User-Agent header and delay
function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function geocodeAddress(address: string): Promise<{ lat: number; lng: number } | null> {
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json`;
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'martian-swiftlogics-driverapp/1.0 (your@email.com)',
        'Accept-Language': 'en',
      },
    });
    const data = await res.json();
    await sleep(1200); // 1.2 second delay to avoid rate limiting
    if (data.length > 0) {
      return { lat: parseFloat(data[0].lat), lng: parseFloat(data[0].lon) };
    }
    return null;
  } catch {
    return null;
  }
}

// Get route polyline from OSRM API
async function getRoutePolyline(coords: { lat: number; lng: number }[]): Promise<{ latitude: number; longitude: number }[]> {
  if (coords.length < 2) return [];
  const points = coords.map(c => `${c.lng},${c.lat}`).join(';');
  const url = `https://router.project-osrm.org/route/v1/driving/${points}?overview=full&geometries=geojson`;
  const res = await fetch(url);
  const data = await res.json();
  if (data.code === 'Ok' && data.routes.length > 0) {
    return data.routes[0].geometry.coordinates.map(([lng, lat]: [number, number]) => ({ latitude: lat, longitude: lng }));
  }
  return [];
}

export default function RouteScreen() {
  const [deliveries, setDeliveries] = useState<Delivery[]>([]);
  const [pendingCoords, setPendingCoords] = useState<{ lat: number; lng: number }[]>([]);
  const [routePolyline, setRoutePolyline] = useState<{ latitude: number; longitude: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await import('@/assets/manifest.json');
        const all: Delivery[] = data.default || data;
        setDeliveries(all);
        // Filter pending deliveries
        const pending = all.filter(d => d.status === 'pending');
        if (pending.length === 0) {
          setError('No pending deliveries found.');
          setPendingCoords([]);
          setRoutePolyline([]);
          return;
        }
        // Geocode addresses
        const coords: { lat: number; lng: number }[] = [];
        let failedAddresses: string[] = [];
        for (const d of pending) {
          const c = await geocodeAddress(d.address);
          if (c) {
            coords.push(c);
          } else {
            failedAddresses.push(d.address);
          }
        }
        setPendingCoords(coords);
        if (coords.length < 2) {
          if (failedAddresses.length > 0) {
            setError(`Could not geocode these addresses: ${failedAddresses.join(', ')}. Need at least two valid delivery locations to show a route.`);
          } else {
            setError('Need at least two valid delivery locations to show a route.');
          }
          setRoutePolyline([]);
          return;
        }
        // Get route polyline
        const polyline = await getRoutePolyline(coords);
        if (polyline.length === 0) {
          setError('Could not fetch route from OSRM.');
        }
        setRoutePolyline(polyline);
      } catch (err) {
        setError('Failed to load route data.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Center map on first delivery or fallback
  const initialRegion = {
    latitude: pendingCoords[0]?.lat || 37.7749,
    longitude: pendingCoords[0]?.lng || -122.4194,
    latitudeDelta: 0.05,
    longitudeDelta: 0.05,
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#00BDD6" style={{ marginTop: 32 }} />
      ) : (
        <View style={{ flex: 1 }}>
          <MapView style={styles.map} initialRegion={initialRegion}>
            <UrlTile
              urlTemplate="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
              maximumZ={19}
              flipY={false}
            />
            {pendingCoords.map((coord, idx) => (
              <Marker
                key={idx}
                coordinate={{ latitude: coord.lat, longitude: coord.lng }}
                title={`Stop ${idx + 1}`}
              />
            ))}
            {routePolyline.length > 1 && (
              <Polyline
                coordinates={routePolyline}
                strokeColor="#00BDD6"
                strokeWidth={4}
              />
            )}
          </MapView>
          {error && (
            <View style={{ position: 'absolute', top: 32, left: 0, right: 0, alignItems: 'center', zIndex: 10 }}>
              <View style={{ backgroundColor: '#ffecec', borderRadius: 8, padding: 12, marginHorizontal: 24 }}>
                <Text style={{ color: '#d8000c', fontWeight: 'bold', textAlign: 'center' }}>{error}</Text>
              </View>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  map: {
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height,
  },
});
