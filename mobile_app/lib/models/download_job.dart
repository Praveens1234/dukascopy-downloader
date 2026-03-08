class DownloadJob {
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
  final List<String> logs;

  DownloadJob({
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
    this.logs = const [],
  });

  factory DownloadJob.fromJson(Map<String, dynamic> json) {
    return DownloadJob(
      id: json['id'] ?? '',
      status: json['status'] ?? 'unknown',
      params: Map<String, dynamic>.from(json['params'] ?? {}),
      progress: (json['progress'] ?? 0).toDouble(),
      totalDays: json['total_days'] ?? 0,
      completedDays: json['completed_days'] ?? 0,
      startedAt: json['started_at'] ?? '',
      finishedAt: json['finished_at'],
      outputFile: json['output_file'],
      error: json['error'],
      logs: List<String>.from(json['logs'] ?? []),
    );
  }

  DownloadJob copyWith({
    String? status,
    double? progress,
    int? completedDays,
    int? totalDays,
    String? finishedAt,
    String? outputFile,
    String? error,
    List<String>? logs,
  }) {
    return DownloadJob(
      id: id,
      status: status ?? this.status,
      params: params,
      progress: progress ?? this.progress,
      totalDays: totalDays ?? this.totalDays,
      completedDays: completedDays ?? this.completedDays,
      startedAt: startedAt,
      finishedAt: finishedAt ?? this.finishedAt,
      outputFile: outputFile ?? this.outputFile,
      error: error ?? this.error,
      logs: logs ?? this.logs,
    );
  }

  String get symbolsDisplay {
    final symbols = params['symbols'];
    if (symbols is List) {
      return symbols.join(', ');
    }
    return 'N/A';
  }

  String get timeframeDisplay => params['timeframe'] ?? 'N/A';
  String get dateRangeDisplay =>
      '${params['start_date'] ?? '?'} to ${params['end_date'] ?? '?'}';

  bool get isRunning => status == 'running' || status == 'pending';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isCancelled => status == 'cancelled';
}
