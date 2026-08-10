import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';
import '../models/job.dart';

class JobDetailsScreen extends StatefulWidget {
  final String jobId;
  const JobDetailsScreen({super.key, required this.jobId});

  @override
  State<JobDetailsScreen> createState() => _JobDetailsScreenState();
}

class _JobDetailsScreenState extends State<JobDetailsScreen> {
  final ApiService _api = ApiService();
  final SocketService _socket = SocketService();

  Job? _job;
  final List<String> _logs = [];
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadJob();
    _initSocket();
  }

  void _initSocket() async {
    await _socket.connect();
    _socket.subscribeToJob(widget.jobId);
    _socket.stream.listen((data) {
      if (!mounted) return;

      if (data['type'] == 'log' && data['job_id'] == widget.jobId) {
        setState(() {
          _logs.add(data['message']);
        });
        _scrollToBottom();
      } else if (data['type'] == 'full_logs' && data['job_id'] == widget.jobId) {
        setState(() {
          _logs.clear();
          _logs.addAll(List<String>.from(data['logs']));
        });
        _scrollToBottom();
      } else if (data['type'] == 'progress' && data['job_id'] == widget.jobId) {
        // Update job state in real-time
        if (_job != null) {
           setState(() {
              _job = Job(
                id: _job!.id,
                status: data['status'],
                params: _job!.params,
                progress: (data['progress'] as num).toDouble(),
                totalDays: data['total_days'],
                completedDays: data['completed_days'],
                startedAt: _job!.startedAt,
                finishedAt: _job!.finishedAt,
                outputFile: _job!.outputFile,
                error: _job!.error,
              );
           });
        }
      }
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _loadJob() async {
    try {
      final job = await _api.getJob(widget.jobId);
      if (mounted) {
        setState(() => _job = job);
      }
    } catch (e) {
      // Handle error
    }
  }

  Future<void> _cancelJob() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Job?'),
        content: const Text('Are you sure you want to stop this download?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('No')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Yes')),
        ],
      ),
    );

    if (confirm == true) {
      await _api.cancelJob(widget.jobId);
      _loadJob();
    }
  }

  @override
  void dispose() {
    _socket.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_job == null) return Scaffold(appBar: AppBar(), body: const Center(child: CircularProgressIndicator()));

    return Scaffold(
      appBar: AppBar(
        title: Text(_job!.params['symbols'] is List ? (_job!.params['symbols'] as List).join(',') : 'Job Details'),
        actions: [
          if (['pending', 'running'].contains(_job!.status))
            IconButton(
              icon: const Icon(Icons.stop_circle_outlined, color: Colors.red),
              onPressed: _cancelJob,
            ),
        ],
      ),
      body: Column(
        children: [
          // Header / Progress
          Container(
            padding: const EdgeInsets.all(16),
            color: Theme.of(context).cardColor,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("Status: ${_job!.status.toUpperCase()}", style: const TextStyle(fontWeight: FontWeight.bold)),
                    Text("${_job!.completedDays}/${_job!.totalDays} days"),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(value: _job!.progress / 100, minHeight: 10, borderRadius: BorderRadius.circular(5)),
                const SizedBox(height: 4),
                Align(alignment: Alignment.centerRight, child: Text("${_job!.progress.toStringAsFixed(1)}%")),
              ],
            ),
          ),
          const Divider(height: 1),
          // Terminal
          Expanded(
            child: Container(
              color: Colors.black,
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(8),
                itemCount: _logs.length,
                itemBuilder: (context, index) {
                  final log = _logs[index];
                  Color color = Colors.greenAccent;
                  if (log.contains('✗') || log.contains('ERROR')) color = Colors.redAccent;
                  else if (log.contains('Warning') || log.contains('⚠')) color = Colors.orangeAccent;
                  else if (log.contains('✓')) color = Colors.green;
                  else if (log.contains('Starting') || log.contains('Download')) color = Colors.blueAccent;
                  else color = Colors.grey[300]!;

                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Text(
                      log,
                      style: TextStyle(color: color, fontFamily: 'monospace', fontSize: 12),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}
