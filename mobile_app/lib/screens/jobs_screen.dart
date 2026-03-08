import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';
import '../models/download_job.dart';

class JobsScreen extends StatefulWidget {
  const JobsScreen({super.key});

  @override
  State<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends State<JobsScreen>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServerProvider>().loadJobs();
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Jobs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: provider.loadJobs,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: provider.loadJobs,
        child: provider.isLoadingJobs && provider.jobs.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : provider.jobs.isEmpty
                ? _buildEmptyState(theme)
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.jobs.length,
                    itemBuilder: (context, index) {
                      return _JobCard(
                        job: provider.jobs[index],
                        onTap: () => _showJobDetail(provider.jobs[index]),
                      );
                    },
                  ),
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.work_off_rounded,
              size: 64,
              color: theme.colorScheme.onSurface.withValues(alpha: 0.2)),
          const SizedBox(height: 16),
          Text('No jobs yet',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.4),
              )),
          const SizedBox(height: 8),
          Text('Start a download from the Download tab',
              style: TextStyle(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.3),
              )),
        ],
      ),
    );
  }

  void _showJobDetail(DownloadJob job) {
    final provider = context.read<ServerProvider>();
    provider.requestJobLogs(job.id);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (context) => _JobDetailSheet(job: job),
    );
  }
}

class _JobCard extends StatelessWidget {
  final DownloadJob job;
  final VoidCallback onTap;

  const _JobCard({required this.job, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Card(
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    _buildStatusIcon(theme),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            job.symbolsDisplay,
                            style: GoogleFonts.inter(
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '${job.timeframeDisplay} | ${job.dateRangeDisplay}',
                            style: TextStyle(
                              fontSize: 12,
                              color: theme.colorScheme.onSurface
                                  .withValues(alpha: 0.5),
                            ),
                          ),
                        ],
                      ),
                    ),
                    _buildStatusBadge(theme),
                  ],
                ),
                if (job.isRunning) ...[
                  const SizedBox(height: 12),
                  _buildProgressBar(theme),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusIcon(ThemeData theme) {
    IconData icon;
    Color color;
    if (job.isRunning) {
      icon = Icons.downloading_rounded;
      color = theme.colorScheme.primary;
    } else if (job.isCompleted) {
      icon = Icons.check_circle_rounded;
      color = const Color(0xFF10B981);
    } else if (job.isFailed) {
      icon = Icons.error_rounded;
      color = theme.colorScheme.error;
    } else if (job.isCancelled) {
      icon = Icons.cancel_rounded;
      color = const Color(0xFFF59E0B);
    } else {
      icon = Icons.pending_rounded;
      color = theme.colorScheme.onSurface.withValues(alpha: 0.4);
    }

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Icon(icon, color: color, size: 22),
    );
  }

  Widget _buildStatusBadge(ThemeData theme) {
    Color color;
    String label;
    if (job.isRunning) {
      color = theme.colorScheme.primary;
      label = '${job.progress.toStringAsFixed(0)}%';
    } else if (job.isCompleted) {
      color = const Color(0xFF10B981);
      label = 'Done';
    } else if (job.isFailed) {
      color = theme.colorScheme.error;
      label = 'Failed';
    } else if (job.isCancelled) {
      color = const Color(0xFFF59E0B);
      label = 'Cancelled';
    } else {
      color = theme.colorScheme.onSurface.withValues(alpha: 0.4);
      label = job.status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(label,
          style: GoogleFonts.inter(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: color,
          )),
    );
  }

  Widget _buildProgressBar(ThemeData theme) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${job.completedDays}/${job.totalDays} days',
              style: TextStyle(
                fontSize: 12,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
              ),
            ),
            Text(
              '${job.progress.toStringAsFixed(1)}%',
              style: GoogleFonts.jetBrainsMono(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.primary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: job.progress / 100,
            minHeight: 6,
          ),
        ),
      ],
    );
  }
}

class _JobDetailSheet extends StatelessWidget {
  final DownloadJob job;

  const _JobDetailSheet({required this.job});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();
    final logs = provider.getJobLogs(job.id);

    // Get the latest job state from provider
    final currentJob =
        provider.jobs.where((j) => j.id == job.id).firstOrNull ?? job;

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12, bottom: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            // Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Job ${currentJob.id}',
                            style: GoogleFonts.inter(
                              fontSize: 18,
                              fontWeight: FontWeight.w700,
                            )),
                        const SizedBox(height: 4),
                        Text(currentJob.symbolsDisplay,
                            style: TextStyle(
                              color: theme.colorScheme.onSurface
                                  .withValues(alpha: 0.6),
                            )),
                      ],
                    ),
                  ),
                  if (currentJob.isRunning)
                    FilledButton.tonalIcon(
                      onPressed: () {
                        provider.cancelJob(currentJob.id);
                        Navigator.pop(context);
                      },
                      icon: const Icon(Icons.stop_rounded, size: 18),
                      label: const Text('Cancel'),
                      style: FilledButton.styleFrom(
                        backgroundColor:
                            theme.colorScheme.error.withValues(alpha: 0.1),
                        foregroundColor: theme.colorScheme.error,
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 12),

            // Progress
            if (currentJob.isRunning)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${currentJob.completedDays}/${currentJob.totalDays} days',
                          style: TextStyle(
                            fontSize: 13,
                            color: theme.colorScheme.onSurface
                                .withValues(alpha: 0.6),
                          ),
                        ),
                        Text(
                          '${currentJob.progress.toStringAsFixed(1)}%',
                          style: GoogleFonts.jetBrainsMono(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: currentJob.progress / 100,
                        minHeight: 8,
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),

            const Divider(),

            // Logs
            Expanded(
              child: Container(
                margin: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF0C0C0C),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: theme.colorScheme.outline.withValues(alpha: 0.2),
                  ),
                ),
                child: Column(
                  children: [
                    // Terminal header
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 10),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A1A1A),
                        borderRadius: const BorderRadius.vertical(
                            top: Radius.circular(12)),
                        border: Border(
                          bottom: BorderSide(
                            color: theme.colorScheme.outline
                                .withValues(alpha: 0.1),
                          ),
                        ),
                      ),
                      child: Row(
                        children: [
                          Container(
                              width: 10,
                              height: 10,
                              decoration: const BoxDecoration(
                                  color: Color(0xFFFF5F56),
                                  shape: BoxShape.circle)),
                          const SizedBox(width: 6),
                          Container(
                              width: 10,
                              height: 10,
                              decoration: const BoxDecoration(
                                  color: Color(0xFFFFBD2E),
                                  shape: BoxShape.circle)),
                          const SizedBox(width: 6),
                          Container(
                              width: 10,
                              height: 10,
                              decoration: const BoxDecoration(
                                  color: Color(0xFF27C93F),
                                  shape: BoxShape.circle)),
                          const Spacer(),
                          Text('Live Logs',
                              style: GoogleFonts.jetBrainsMono(
                                fontSize: 12,
                                color: const Color(0xFF888888),
                              )),
                        ],
                      ),
                    ),
                    // Log content
                    Expanded(
                      child: logs.isEmpty
                          ? Center(
                              child: Text('Waiting for logs...',
                                  style: GoogleFonts.jetBrainsMono(
                                    fontSize: 13,
                                    color: const Color(0xFF555555),
                                  )))
                          : ListView.builder(
                              controller: scrollController,
                              padding: const EdgeInsets.all(12),
                              itemCount: logs.length,
                              itemBuilder: (context, index) {
                                return _buildLogLine(logs[index], theme);
                              },
                            ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildLogLine(String line, ThemeData theme) {
    Color color = const Color(0xFFD4D4D4);
    if (line.contains('\u2713') || line.contains('Complete')) {
      color = const Color(0xFF10B981);
    } else if (line.contains('\u2717') || line.contains('ERROR') || line.contains('FATAL')) {
      color = const Color(0xFFEF4444);
    } else if (line.contains('\u26A1') || line.contains('Starting') || line.contains('\u2500')) {
      color = const Color(0xFF3B82F6);
    } else if (line.contains('\u26A0')) {
      color = const Color(0xFFF59E0B);
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 1),
      child: Text(
        line,
        style: GoogleFonts.jetBrainsMono(
          fontSize: 12,
          color: color,
          height: 1.5,
        ),
      ),
    );
  }
}
