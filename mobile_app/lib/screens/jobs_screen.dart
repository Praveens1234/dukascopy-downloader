import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/job.dart';
import 'job_detail_screen.dart';

class JobsScreen extends StatefulWidget {
  const JobsScreen({super.key});

  @override
  State<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends State<JobsScreen> {
  List<Job> _jobs = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    setState(() => _isLoading = true);
    try {
      final apiService = context.read<ApiService>();
      final jobs = await apiService.getJobs();
      setState(() => _jobs = jobs);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading jobs: $e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Download Jobs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadJobs,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _jobs.isEmpty
              ? const Center(child: Text('No jobs found'))
              : ListView.builder(
                  itemCount: _jobs.length,
                  itemBuilder: (_, i) => _buildJobCard(_jobs[i]),
                ),
    );
  }

  Widget _buildJobCard(Job job) {
    return Card(
      margin: const EdgeInsets.all(8),
      child: ListTile(
        title: Text(job.params['symbols']?.join(", ") ?? "Unknown"),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${job.status}'),
            if (job.progress > 0) Text('Progress: ${job.progress.toStringAsFixed(1)}%'),
          ],
        ),
        trailing: Icon(
          job.isRunning ? Icons.hourglass_empty : (job.isCompleted ? Icons.check_circle : Icons.error),
          color: job.isRunning ? Colors.orange : (job.isCompleted ? Colors.green : Colors.red),
        ),
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => JobDetailScreen(jobId: job.id)),
        ),
      ),
    );
  }
}
