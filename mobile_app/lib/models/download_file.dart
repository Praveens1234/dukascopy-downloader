class DownloadFile {
  final String name;
  final int size;
  final String sizeHuman;
  final String modified;

  DownloadFile({
    required this.name,
    required this.size,
    required this.sizeHuman,
    required this.modified,
  });

  factory DownloadFile.fromJson(Map<String, dynamic> json) {
    return DownloadFile(
      name: json['name'] ?? '',
      size: json['size'] ?? 0,
      sizeHuman: json['size_human'] ?? '0 B',
      modified: json['modified'] ?? '',
    );
  }
}
