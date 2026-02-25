import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/job.dart';
import 'new_job_screen.dart';
import 'job_details_screen.dart';
import 'files_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _api = ApiService();
  List<Job> _jobs = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    try {
      final jobs = await _api.getJobs();
      if (mounted) {
        setState(() {
          _jobs = jobs;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'completed': return Colors.green;
      case 'running': return Colors.blue;
      case 'failed': return Colors.red;
      case 'cancelled': return Colors.orange;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.folder),
            onPressed: () {
               Navigator.push(context, MaterialPageRoute(builder: (_) => const FilesScreen()));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadJobs,
        child: _isLoading && _jobs.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : _jobs.isEmpty
                ? Center(
                    child: SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.assignment_outlined, size: 64, color: Colors.grey),
                          const SizedBox(height: 16),
                          Text('No jobs yet', style: Theme.of(context).textTheme.titleLarge),
                          const SizedBox(height: 8),
                          const Text('Start a new download to see it here'),
                        ],
                      ),
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _jobs.length,
                    itemBuilder: (context, index) {
                      final job = _jobs[index];
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        elevation: 2,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        child: InkWell(
                          onTap: () async {
                            await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => JobDetailsScreen(jobId: job.id),
                              ),
                            );
                            _loadJobs();
                          },
                          borderRadius: BorderRadius.circular(12),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        (job.params['symbols'] as List).join(', '),
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: _getStatusColor(job.status).withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(color: _getStatusColor(job.status).withOpacity(0.3)),
                                      ),
                                      child: Text(
                                        job.status.toUpperCase(),
                                        style: TextStyle(
                                          color: _getStatusColor(job.status),
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  '${job.params['start_date']} → ${job.params['end_date']}',
                                  style: TextStyle(color: Colors.grey[600], fontSize: 13),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Timeframe: ${job.params['timeframe']}',
                                  style: TextStyle(color: Colors.grey[600], fontSize: 13),
                                ),
                                const SizedBox(height: 12),
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(4),
                                  child: LinearProgressIndicator(
                                    value: job.progress / 100,
                                    backgroundColor: Colors.grey[200],
                                    valueColor: AlwaysStoppedAnimation<Color>(_getStatusColor(job.status)),
                                    minHeight: 6,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      '${job.completedDays}/${job.totalDays} days',
                                      style: TextStyle(color: Colors.grey[500], fontSize: 11),
                                    ),
                                    Text(
                                      '${job.progress.toStringAsFixed(1)}%',
                                      style: TextStyle(color: _getStatusColor(job.status), fontSize: 11, fontWeight: FontWeight.bold),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
                  ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          await Navigator.push(context, MaterialPageRoute(builder: (_) => const NewJobScreen()));
          _loadJobs();
        },
        label: const Text('New Job'),
        icon: const Icon(Icons.add),
      ),
    );
  }
}
