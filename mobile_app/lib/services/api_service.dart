import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/server_config.dart';
import '../models/download_job.dart';
import '../models/download_file.dart';

class ApiService {
  String _baseUrl;

  ApiService({String baseUrl = 'http://192.168.1.100:8000'})
      : _baseUrl = baseUrl;

  String get baseUrl => _baseUrl;

  void updateBaseUrl(String url) {
    _baseUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
  }

  Future<bool> testConnection() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/api/config'))
          .timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<ServerConfig> getConfig() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/config'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      return ServerConfig.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to load config: ${response.statusCode}');
  }

  Future<String> startDownload({
    required List<String> symbols,
    required String startDate,
    required String endDate,
    String timeframe = 'M1',
    int threads = 5,
    String dataSource = 'auto',
    String priceType = 'BID',
    String volumeType = 'TOTAL',
    String? customTf,
  }) async {
    final body = {
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

    final response = await http
        .post(
          Uri.parse('$_baseUrl/api/download'),
          headers: {'Content-Type': 'application/json'},
          body: json.encode(body),
        )
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['job_id'] as String;
    }
    throw Exception('Failed to start download: ${response.statusCode}');
  }

  Future<List<DownloadJob>> getJobs() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/jobs'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((j) => DownloadJob.fromJson(j)).toList();
    }
    throw Exception('Failed to load jobs: ${response.statusCode}');
  }

  Future<DownloadJob> getJob(String jobId) async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/jobs/$jobId'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      return DownloadJob.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to load job: ${response.statusCode}');
  }

  Future<bool> cancelJob(String jobId) async {
    final response = await http
        .post(Uri.parse('$_baseUrl/api/jobs/$jobId/cancel'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['success'] == true;
    }
    return false;
  }

  Future<List<DownloadFile>> getFiles() async {
    final response = await http
        .get(Uri.parse('$_baseUrl/api/files'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((f) => DownloadFile.fromJson(f)).toList();
    }
    throw Exception('Failed to load files: ${response.statusCode}');
  }

  Future<bool> deleteFile(String filename) async {
    final response = await http
        .delete(Uri.parse('$_baseUrl/api/files/$filename'))
        .timeout(const Duration(seconds: 10));
    return response.statusCode == 200;
  }

  String getFileDownloadUrl(String filename) {
    return '$_baseUrl/api/files/$filename';
  }
}
