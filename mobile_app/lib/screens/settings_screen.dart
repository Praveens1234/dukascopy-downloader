import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/server_config_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _urlController = TextEditingController();
  bool _isTesting = false;

  @override
  void initState() {
    super.initState();
    final serverConfig = context.read<ServerConfigService>();
    _urlController.text = serverConfig.serverUrl;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildServerCard(),
            const SizedBox(height: 16),
            _buildAboutCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildServerCard() {
    final serverConfig = context.watch<ServerConfigService>();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Server Connection', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'Server URL',
                hintText: 'http://192.168.1.100:8000',
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _isTesting ? null : _testConnection,
                    child: _isTesting
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Test Connection'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: FilledButton(
                    onPressed: _saveSettings,
                    child: const Text('Save'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  serverConfig.isConnected ? Icons.cloud_done : Icons.cloud_off,
                  color: serverConfig.isConnected ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  serverConfig.isConnected ? 'Connected' : 'Disconnected',
                  style: TextStyle(
                    color: serverConfig.isConnected ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAboutCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('About', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            const Text('Version: 1.0.0'),
            const Text('Backend: Dukascopy Downloader v1.0.0'),
          ],
        ),
      ),
    );
  }

  Future<void> _testConnection() async {
    setState(() => _isTesting = true);
    try {
      final apiService = context.read<ApiService>();
      final serverConfig = context.read<ServerConfigService>();
      apiService.setServerUrl(_urlController.text);
      await apiService.getConfig();
      serverConfig.setConnectionStatus(true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Connection successful!')),
        );
      }
    } catch (e) {
      final serverConfig = context.read<ServerConfigService>();
      serverConfig.setConnectionStatus(false, error: e.toString());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connection failed: $e')),
        );
      }
    } finally {
      setState(() => _isTesting = false);
    }
  }

  void _saveSettings() {
    final serverConfig = context.read<ServerConfigService>();
    serverConfig.setServerUrl(_urlController.text);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings saved!')),
    );
  }
}
