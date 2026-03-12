import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';
import '../models/job.dart';

class JobDetailScreen extends StatefulWidget {
  final String jobId;
  const JobDetailScreen({super.key, required this.jobId});

  @override
  State<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends State<JobDetailScreen> {
  Job? _job;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadJob();
    _connectWebSocket();
  }

  void _connectWebSocket() {
    final wsService = context.read<WebSocketService>();
    final serverConfig = context.read<ServerConfigService>();
    final wsUrl = serverConfig.serverUrl.replaceAll('http', 'ws');
    wsService.connect(wsUrl);
  }

  Future<void> _loadJob() async {
    try {
      final apiService = context.read<ApiService>();
      final job = await apiService.getJob(widget.jobId);
      setState(() {
        _job = job;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading job: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Download Progress'),
        actions: [
          IconButton(
            icon: const Icon(Icons.stop),
            onPressed: _job?.isRunning ?? false ? _cancelJob : null,
          ),
        ],
      ),
      body: _job != null ? _buildContent() : const Center(child: Text('Job not found')),
    );
  }

  Widget _buildContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildProgressCard(),
          const SizedBox(height: 16),
          _buildConfigCard(),
          const SizedBox(height: 16),
          _buildLogsCard(),
        ],
      ),
    );
  }

  Widget _buildProgressCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              _job!.status.toUpperCase(),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: _job!.isRunning ? Colors.blue : (_job!.isCompleted ? Colors.green : Colors.red),
              ),
            ),
            const SizedBox(height: 16),
            LinearProgressIndicator(value: _job!.progress / 100),
            const SizedBox(height: 8),
            Text('${_job!.progress.toStringAsFixed(1)}%'),
            Text('${_job!.completedDays} / ${_job!.totalDays} days completed'),
          ],
        ),
      ),
    );
  }

  Widget _buildConfigCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Configuration', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Symbols: ${_job!.params['symbols']?.join(", ") ?? "N/A"}'),
            Text('Period: ${_job!.params['start_date']} to ${_job!.params['end_date']}'),
            Text('Timeframe: ${_job!.params['timeframe']}'),
          ],
        ),
      ),
    );
  }

  Widget _buildLogsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Logs', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              height: 300,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListView.builder(
                itemCount: _job!.logs.length,
                itemBuilder: (_, i) => Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: Text(_job!.logs[i], style: const TextStyle(fontSize: 12)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _cancelJob() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Cancel Download?'),
        content: const Text('Are you sure you want to cancel this download?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('No'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Yes'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        final apiService = context.read<ApiService>();
        await apiService.cancelJob(widget.jobId);
        _loadJob();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error cancelling job: $e')),
          );
        }
      }
    }
  }
}
