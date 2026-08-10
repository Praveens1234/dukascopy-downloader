import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        children: [
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Theme',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          RadioListTile<ThemeMode>(
            title: const Text('System Default'),
            value: ThemeMode.system,
            groupValue: themeProvider.themeMode,
            onChanged: (ThemeMode? value) {
              if (value != null) {
                themeProvider.setThemeMode(value);
              }
            },
          ),
          RadioListTile<ThemeMode>(
            title: const Text('Light Theme'),
            value: ThemeMode.light,
            groupValue: themeProvider.themeMode,
            onChanged: (ThemeMode? value) {
              if (value != null) {
                themeProvider.setThemeMode(value);
              }
            },
          ),
          RadioListTile<ThemeMode>(
            title: const Text('Dark Theme'),
            value: ThemeMode.dark,
            groupValue: themeProvider.themeMode,
            onChanged: (ThemeMode? value) {
              if (value != null) {
                themeProvider.setThemeMode(value);
              }
            },
          ),
        ],
      ),
    );
  }
}
