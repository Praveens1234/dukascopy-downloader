import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';
import 'download_screen.dart';
import 'jobs_screen.dart';
import 'files_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  final _screens = const [
    DownloadScreen(),
    JobsScreen(),
    FilesScreen(),
    SettingsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    // Check connection on entry
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = context.read<ServerProvider>();
      if (!provider.isConnected) {
        Navigator.of(context).pushReplacementNamed('/');
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        transitionBuilder: (child, animation) {
          return FadeTransition(
            opacity: animation,
            child: child,
          );
        },
        child: _screens[_currentIndex],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        height: 72,
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.download_rounded,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            selectedIcon: Icon(Icons.download_rounded,
                color: theme.colorScheme.primary),
            label: 'Download',
          ),
          NavigationDestination(
            icon: Icon(Icons.work_history_rounded,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            selectedIcon: Icon(Icons.work_history_rounded,
                color: theme.colorScheme.primary),
            label: 'Jobs',
          ),
          NavigationDestination(
            icon: Icon(Icons.folder_rounded,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            selectedIcon:
                Icon(Icons.folder_rounded, color: theme.colorScheme.primary),
            label: 'Files',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_rounded,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            selectedIcon: Icon(Icons.settings_rounded,
                color: theme.colorScheme.primary),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}
