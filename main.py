import 'package:flutter/material.dart';

void main() {
  runApp(const AerisAI());
}

class AerisAI extends StatelessWidget {
  const AerisAI({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Aeris AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: Colors.black,
        primaryColor: Colors.green,
      ),
      home: const HomeScreen(),
    );
  }
}

#/* -------------------- MOCK DATA -------------------- */

final rooms = [
  {"name": "Kitchen", "risk": "danger"},
  {"name": "Garage", "risk": "warning"},
  {"name": "Bedroom", "risk": "normal"},
  {"name": "Basement", "risk": "normal"},
];

Color riskColor(String risk) {
  switch (risk) {
    case "danger":
      return Colors.red;
    case "warning":
      return Colors.orange;
    default:
      return Colors.green;
  }
}

#/* -------------------- HOME SCREEN -------------------- */

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Aeris AI")),
      body: Center(
        child: ElevatedButton(
          child: const Text("Start"),
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const RoomOverview()),
            );
          },
        ),
      ),
    );
  }
}

#/* -------------------- ROOM OVERVIEW -------------------- */

class RoomOverview extends StatelessWidget {
  const RoomOverview({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Room Sensors")),
      body: ListView(
        children: rooms.map((room) {
          return Card(
            color: Colors.grey[900],
            child: ListTile(
              title: Text(room["name"] as String),
              trailing: Icon(
                Icons.circle,
                color: riskColor(room["risk"] as String),
              ),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => SensorDetail(room["name"] as String),
                  ),
                );
              },
            ),
          );
        }).toList(),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: Colors.red,
        child: const Icon(Icons.warning),
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AlertsScreen()),
          );
        },
      ),
    );
  }
}

#/* -------------------- SENSOR DETAIL -------------------- */

class SensorDetail extends StatelessWidget {
  final String room;
  const SensorDetail(this.room, {super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("$room Sensors")),
      body: Column(
        children: [
          sensorCard("Carbon Monoxide", "Normal", Colors.green, context, COPage()),
          sensorCard("Chlorine", "Warning", Colors.orange, context, ChlorinePage()),
          sensorCard("Hydrogen Sulfide", "Danger", Colors.red, context, H2SPage()),
        ],
      ),
    );
  }

  Widget sensorCard(
    String name,
    String status,
    Color color,
    BuildContext context,
    Widget page,
  ) {
    return Card(
      color: Colors.grey[900],
      child: ListTile(
        title: Text(name),
        subtitle: Text(status),
        trailing: Icon(Icons.chevron_right, color: color),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => page),
          );
        },
      ),
    );
  }
}



class AlertsScreen extends StatelessWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Alerts")),
      body: ListView(
        children: const [
          ListTile(
            leading: Icon(Icons.warning, color: Colors.red),
            title: Text("Hydrogen Sulfide detected in Kitchen"),
          ),
          ListTile(
            leading: Icon(Icons.build, color: Colors.orange),
            title: Text("Sensor maintenance recommended"),
          ),
        ],
      ),
    );
  }
}

/* -------------------- GAS SCREENS -------------------- */

class COPage extends StatelessWidget {
  const COPage({super.key});

  @override
  Widget build(BuildContext context) {
    return gasTemplate(
      "Carbon Monoxide",
      "Safe levels detected",
      Colors.green,
    );
  }
}

class ChlorinePage extends StatelessWidget {
  const ChlorinePage({super.key});

  @override
  Widget build(BuildContext context) {
    return gasTemplate(
      "Chlorine",
      "Moderate levels detected",
      Colors.orange,
    );
  }
}

class H2SPage extends StatelessWidget {
  const H2SPage({super.key});

  @override
  Widget build(BuildContext context) {
    return gasTemplate(
      "Hydrogen Sulfide",
      "Dangerous levels detected",
      Colors.red,
    );
  }
}

Widget gasTemplate(String gas, String status, Color color) {
  return Scaffold(
    appBar: AppBar(title: Text(gas)),
    body: Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud, size: 80, color: color),
          const SizedBox(height: 20),
          Text(status, style: TextStyle(fontSize: 18, color: color)),
          const SizedBox(height: 20),
          const Text("Weather: Clear\nAir Quality: Moderate"),
        ],
      ),
    ),
  );
}



