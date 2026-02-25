class Job {
  final String id;
  final String status;
  final Map<String, dynamic> params;
  final double progress;
  final int totalDays;
  final int completedDays;
  final String startedAt;
  final String? finishedAt;
  final String? outputFile;
  final String? error;

  Job({
    required this.id,
    required this.status,
    required this.params,
    required this.progress,
    required this.totalDays,
    required this.completedDays,
    required this.startedAt,
    this.finishedAt,
    this.outputFile,
    this.error,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['id'],
      status: json['status'],
      params: json['params'] ?? {},
      progress: (json['progress'] as num?)?.toDouble() ?? 0.0,
      totalDays: json['total_days'] ?? 0,
      completedDays: json['completed_days'] ?? 0,
      startedAt: json['started_at'],
      finishedAt: json['finished_at'],
      outputFile: json['output_file'],
      error: json['error'],
    );
  }
}
