class ServerConfig {
  final List<String> symbols;
  final List<String> timeframes;
  final int defaultThreads;
  final int maxThreads;
  final List<String> volumeTypes;

  ServerConfig({
    required this.symbols,
    required this.timeframes,
    required this.defaultThreads,
    required this.maxThreads,
    required this.volumeTypes,
  });

  factory ServerConfig.fromJson(Map<String, dynamic> json) {
    return ServerConfig(
      symbols: List<String>.from(json['symbols'] ?? []),
      timeframes: List<String>.from(json['timeframes'] ?? []),
      defaultThreads: json['default_threads'] ?? 5,
      maxThreads: json['max_threads'] ?? 30,
      volumeTypes: List<String>.from(json['volume_types'] ?? []),
    );
  }
}
