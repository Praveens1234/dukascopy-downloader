import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/server_config_service.dart';
import '../models/download_config.dart';
import 'job_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final List<String> _selectedSymbols = ['EURUSD'];
  final List<String> _availableSymbols = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
    'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD', 'XAGUSD'
  ];
  DateTime _startDate = DateTime(2024, 1, 1);
  DateTime _endDate = DateTime(2024, 12, 31);
  String _timeframe = 'M1';
  int _threads = 5;
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dukascopy Downloader'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _navigateToSettings(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildServerStatusCard(),
            const SizedBox(height: 16),
            _buildSymbolsCard(),
            const SizedBox(height: 16),
            _buildDateRangeCard(),
            const SizedBox(height: 16),
            _buildTimeframeCard(),
            const SizedBox(height: 16),
            _buildAdvancedOptionsCard(),
            const SizedBox(height: 24),
            _buildStartButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildServerStatusCard() {
    final serverConfig = context.watch<ServerConfigService>();
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              serverConfig.isConnected ? Icons.cloud_done : Icons.cloud_off,
              color: serverConfig.isConnected ? Colors.green : Colors.red,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    serverConfig.isConnected ? 'Connected' : 'Disconnected',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    serverConfig.serverUrl,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSymbolsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Symbols', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _availableSymbols.map((symbol) {
                final isSelected = _selectedSymbols.contains(symbol);
                return FilterChip(
                  label: Text(symbol),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _selectedSymbols.add(symbol);
                      } else {
                        _selectedSymbols.remove(symbol);
                      }
                    });
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDateRangeCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Date Range', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    readOnly: true,
                    decoration: const InputDecoration(
                      labelText: 'From',
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    controller: TextEditingController(
                      text: _startDate.toString().split(' ')[0],
                    ),
                    onTap: () => _selectDate(isStart: true),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    readOnly: true,
                    decoration: const InputDecoration(
                      labelText: 'To',
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    controller: TextEditingController(
                      text: _endDate.toString().split(' ')[0],
                    ),
                    onTap: () => _selectDate(isStart: false),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeframeCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Timeframe', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _timeframe,
              decoration: const InputDecoration(labelText: 'Select Timeframe'),
              items: ['TICK', 'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
                  .map((tf) => DropdownMenuItem(value: tf, child: Text(tf)))
                  .toList(),
              onChanged: (value) => setState(() => _timeframe = value!),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdvancedOptionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Advanced Options', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text('Threads: $_threads'),
            Slider(
              value: _threads.toDouble(),
              min: 1,
              max: 30,
              divisions: 29,
              label: _threads.toString(),
              onChanged: (value) => setState(() => _threads = value.toInt()),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStartButton() {
    return FilledButton(
      onPressed: _isLoading ? null : _startDownload,
      child: _isLoading
          ? const SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Text('START DOWNLOAD', style: TextStyle(fontSize: 16)),
            ),
    );
  }

  Future<void> _selectDate({required bool isStart}) async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
      initialDate: isStart ? _startDate : _endDate,
    );
    if (picked != null) {
      setState(() {
        if (isStart) _startDate = picked;
        else _endDate = picked;
      });
    }
  }

  Future<void> _startDownload() async {
    setState(() => _isLoading = true);
    try {
      final apiService = context.read<ApiService>();
      final config = DownloadConfig(
        symbols: _selectedSymbols,
        startDate: _startDate.toString().split(' ')[0],
        endDate: _endDate.toString().split(' ')[0],
        timeframe: _timeframe,
        threads: _threads,
      );
      final result = await apiService.startDownload(config);
      final jobId = result['job_id'];
      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => JobDetailScreen(jobId: jobId!),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _navigateToSettings() {
    Navigator.pushNamed(context, '/settings');
  }
}
