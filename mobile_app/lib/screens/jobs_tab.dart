import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class JobsTab extends StatelessWidget {
  final String serverUrl;
  final List<dynamic> jobs;
  final VoidCallback onRefresh;
  final Function(String) onViewLogs;

  const JobsTab({
    super.key,
    required this.serverUrl,
    required this.jobs,
    required this.onRefresh,
    required this.onViewLogs,
  });

  Future<void> _cancelJob(BuildContext context, String jobId) async {
    final bool? confirm = await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancel Job'),
        content: const Text('Are you sure you want to cancel this download?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('No')),
          TextButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Yes')),
        ],
      ),
    );

    if (confirm == true) {
      try {
        final res = await http.post(Uri.parse('$serverUrl/api/jobs/$jobId/cancel'));
        if (res.statusCode == 200) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Job cancelled')));
          }
          onRefresh();
        }
      } catch (e) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (jobs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.list_alt, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No jobs yet', style: TextStyle(color: Colors.grey)),
            TextButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh'),
            )
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: jobs.length,
        itemBuilder: (context, index) {
          final job = jobs[index];
          final params = job['params'] ?? {};
          final symbols = (params['symbols'] as List<dynamic>?)?.join(', ') ?? '—';
          final tf = params['timeframe'] ?? '—';
          final isRunning = job['status'] == 'pending' || job['status'] == 'running';

          Color statusColor;
          IconData statusIcon;
          if (job['status'] == 'completed') {
            statusColor = Colors.greenAccent;
            statusIcon = Icons.check_circle;
          } else if (job['status'] == 'failed') {
            statusColor = Colors.redAccent;
            statusIcon = Icons.error;
          } else if (job['status'] == 'cancelled') {
            statusColor = Colors.orangeAccent;
            statusIcon = Icons.cancel;
          } else {
            statusColor = const Color(0xFF3B82F6);
            statusIcon = Icons.sync;
          }

          final progress = (job['progress'] as num).toDouble();

          return Card(
            margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
            child: InkWell(
              onTap: () => onViewLogs(job['id']),
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(statusIcon, color: statusColor, size: 28),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('$symbols — $tf', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                              const SizedBox(height: 4),
                              Text('${params['start_date']} to ${params['end_date']}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                            ],
                          ),
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text('${progress.round()}%', style: TextStyle(color: statusColor, fontWeight: FontWeight.bold, fontSize: 16)),
                            if (isRunning)
                              IconButton(
                                icon: const Icon(Icons.stop_circle, color: Colors.redAccent),
                                padding: EdgeInsets.zero,
                                constraints: const BoxConstraints(),
                                onPressed: () => _cancelJob(context, job['id']),
                              ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    LinearProgressIndicator(
                      value: progress / 100,
                      backgroundColor: Colors.white12,
                      color: statusColor,
                      minHeight: 6,
                      borderRadius: BorderRadius.circular(3),
                    ),
                    if (job['error'] != null) ...[
                      const SizedBox(height: 8),
                      Text('Error: ${job['error']}', style: const TextStyle(color: Colors.redAccent, fontSize: 12), maxLines: 2, overflow: TextOverflow.ellipsis),
                    ]
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
