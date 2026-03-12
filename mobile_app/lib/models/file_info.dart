class FileInfo {
  final String name;
  final int size;
  final String modified;

  FileInfo({
    required this.name,
    required this.size,
    required this.modified,
  });

  factory FileInfo.fromJson(Map<String, dynamic> json) {
    return FileInfo(
      name: json['name'] ?? '',
      size: json['size'] ?? 0,
      modified: json['modified'] ?? '',
    );
  }

  String get sizeFormatted {
    const units = ['B', 'KB', 'MB', 'GB'];
    double size = this.size.toDouble();
    int unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return '${size.toStringAsFixed(1)} ${units[unitIndex]}';
  }
}
