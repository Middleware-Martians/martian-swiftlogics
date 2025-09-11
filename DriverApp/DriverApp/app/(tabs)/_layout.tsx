import { Tabs } from 'expo-router';
import React from 'react';
import { Platform } from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarBackground: TabBarBackground,
        tabBarStyle: Platform.select({
          ios: {
            // Use a transparent background on iOS to show the blur effect
            position: 'absolute',
          },
          default: {},
        }),
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="house.fill" color={color} />,
        }}
      />
        <Tabs.Screen
          name="manifest"
          options={{
            title: 'Manifest',
            tabBarIcon: ({ color }) => <IconSymbol size={28} name="doc.text.fill" color={color} />,
          }}
        />
        <Tabs.Screen
          name="route"
          options={{
            title: 'Route',
            tabBarIcon: ({ color }) => <IconSymbol size={28} name="map.fill" color={color} />,
          }}
        />
        <Tabs.Screen
          name="delivery-updates"
          options={{
            title: 'Delivery Updates',
            tabBarIcon: ({ color }) => <IconSymbol size={28} name="bell.fill" color={color} />,
          }}
        />
        <Tabs.Screen
          name="proof-of-delivery"
          options={{
            title: 'Proof of Delivery',
            tabBarIcon: ({ color }) => <IconSymbol size={28} name="checkmark.seal.fill" color={color} />,
          }}
        />
    </Tabs>
  );
}
