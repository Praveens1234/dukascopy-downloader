import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/server_config_service.dart';
import 'services/api_service.dart';
import 'screens/home_screen.dart';
import 'screens/jobs_screen.dart';
import 'screens/files_screen.dart';
import 'screens/settings_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const DukascopyApp());
}

class DukascopyApp extends StatelessWidget {
  const DukascopyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ServerConfigService()),
        ChangeNotifierProvider(create: (_) => ApiService()),
      ],
      child: Consumer<ServerConfigService>(
        builder: (context, serverConfig, _) {
          return MaterialApp(
            title: 'Dukascopy Downloader',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: ThemeMode.system,
            home: const MainNavigationScreen(),
          );
        },
      ),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const JobsScreen(),
    const FilesScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.download_outlined),
            label: 'Download',
            selectedIcon: Icon(Icons.download),
          ),
          NavigationDestination(
            icon: Icon(Icons.list_outlined),
            label: 'Jobs',
            selectedIcon: Icon(Icons.list),
          ),
          NavigationDestination(
            icon: Icon(Icons.folder_outlined),
            label: 'Files',
            selectedIcon: Icon(Icons.folder),
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            label: 'Settings',
            selectedIcon: Icon(Icons.settings),
          ),
        ],
      ),
    );
  }
}
