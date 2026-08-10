class DownloadRequest {
  final List<String> symbols;
  final String startDate;
  final String endDate;
  final String timeframe;
  final int threads;
  final String dataSource;
  final String priceType;
  final String volumeType;
  final String? customTf;

  DownloadRequest({
    required this.symbols,
    required this.startDate,
    required this.endDate,
    required this.timeframe,
    required this.threads,
    required this.dataSource,
    required this.priceType,
    required this.volumeType,
    this.customTf,
  });

  Map<String, dynamic> toJson() {
    return {
      'symbols': symbols,
      'start_date': startDate,
      'end_date': endDate,
      'timeframe': timeframe,
      'threads': threads,
      'data_source': dataSource,
      'price_type': priceType,
      'volume_type': volumeType,
      'custom_tf': customTf,
    };
  }
}
