class Job {
  final String id;
  final String status;
  final Map<String, dynamic> params;
  final double progress;
  final int totalDays;
  final int completedDays;
  final List<String> logs;
  final String? startedAt;
  final String? finishedAt;
  final String? outputFile;
  final String? error;

  Job({
    required this.id,
    required this.status,
    required this.params,
    this.progress = 0,
    this.totalDays = 0,
    this.completedDays = 0,
    this.logs = const [],
    this.startedAt,
    this.finishedAt,
    this.outputFile,
    this.error,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['id'] ?? '',
      status: json['status'] ?? 'unknown',
      params: json['params'] ?? {},
      progress: (json['progress'] ?? 0).toDouble(),
      totalDays: json['total_days'] ?? 0,
      completedDays: json['completed_days'] ?? 0,
      logs: json['logs'] != null ? List<String>.from(json['logs']) : [],
      startedAt: json['started_at'],
      finishedAt: json['finished_at'],
      outputFile: json['output_file'],
      error: json['error'],
    );
  }

  bool get isRunning => status == 'running' || status == 'pending';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isCancelled => status == 'cancelled';
}
