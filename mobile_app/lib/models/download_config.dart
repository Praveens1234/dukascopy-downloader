class DownloadConfig {
  final List<String> symbols;
  final String startDate;
  final String endDate;
  final String timeframe;
  final int threads;
  final String dataSource;
  final String priceType;
  final String volumeType;
  final String? customTf;

  DownloadConfig({
    required this.symbols,
    required this.startDate,
    required this.endDate,
    this.timeframe = 'M1',
    this.threads = 5,
    this.dataSource = 'auto',
    this.priceType = 'BID',
    this.volumeType = 'TOTAL',
    this.customTf,
  });

  Map<String, dynamic> toJson() => {
    'symbols': symbols,
    'start_date': startDate,
    'end_date': endDate,
    'timeframe': timeframe,
    'threads': threads,
    'data_source': dataSource,
    'price_type': priceType,
    'volume_type': volumeType,
    if (customTf != null) 'custom_tf': customTf,
  };
}
