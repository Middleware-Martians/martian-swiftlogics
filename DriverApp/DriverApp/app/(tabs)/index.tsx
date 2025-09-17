import { View, Text, StyleSheet } from 'react-native';

export default function HomeScreen() {
  // Replace with actual driver name from state, context, or props if available
  const driverName = "John Doe";

  return (
    <View style={styles.container}>
      <Text style={styles.welcome}>Welcome to the Driver App!</Text>
      <Text style={styles.name}>Driver: {driverName}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  welcome: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  name: {
    fontSize: 20,
    color: '#333',
  },
});