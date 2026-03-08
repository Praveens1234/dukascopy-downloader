import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/connection_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final prefs = await SharedPreferences.getInstance();
  final lastServerUrl = prefs.getString('server_url');

  runApp(MyApp(initialUrl: lastServerUrl));
}

class MyApp extends StatelessWidget {
  final String? initialUrl;

  const MyApp({super.key, this.initialUrl});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dukascopy Downloader',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF3B82F6), // Matches web accent color
          brightness: Brightness.dark,
          background: const Color(0xFF0A0E17), // --bg-primary
          surface: const Color(0xFF1A2234), // --bg-card
        ),
        scaffoldBackgroundColor: const Color(0xFF0A0E17),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF111827),
          elevation: 0,
        ),
      ),
      // If we have a saved URL, go to Home, else Connection Screen
      home: initialUrl != null && initialUrl!.isNotEmpty
          ? HomeScreen(serverUrl: initialUrl!)
          : const ConnectionScreen(),
    );
  }
}
