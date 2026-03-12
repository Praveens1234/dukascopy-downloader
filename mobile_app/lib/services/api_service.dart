import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/download_config.dart';
import '../models/job.dart';
import '../models/file_info.dart';
import 'server_config_service.dart';

class ApiService extends ChangeNotifier {
  String _baseUrl = '';
  bool _isLoading = false;
  String? _error;

  String get baseUrl => _baseUrl;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void setServerUrl(String url) {
    _baseUrl = url.endsWith('/') ? url : '$url/';
    _error = null;
  }

  Future<T> _wrapRequest<T>(Future<T> Function() request) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final result = await request();
      return result;
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<Map<String, dynamic>> getConfig() async {
    final response = await http.get(Uri.parse('$_baseUrl/api/config'));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load config: ${response.statusCode}');
  }

  Future<Map<String, String>> startDownload(DownloadConfig config) async {
    final response = await http.post(
      Uri.parse('${_baseUrl}api/download'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(config.toJson()),
    );
    if (response.statusCode == 200) {
      return Map<String, String>.from(json.decode(response.body));
    }
    throw Exception('Failed to start download: ${response.statusCode}');
  }

  Future<List<Job>> getJobs() async {
    final response = await http.get(Uri.parse('${_baseUrl}api/jobs'));
    if (response.statusCode == 200) {
      final List<dynamic> jobsJson = json.decode(response.body);
      return jobsJson.map((json) => Job.fromJson(json)).toList();
    }
    throw Exception('Failed to load jobs: ${response.statusCode}');
  }

  Future<Job> getJob(String jobId) async {
    final response = await http.get(Uri.parse('${_baseUrl}api/jobs/$jobId'));
    if (response.statusCode == 200) {
      return Job.fromJson(json.decode(response.body));
    }
    throw Exception('Failed to load job: ${response.statusCode}');
  }

  Future<void> cancelJob(String jobId) async {
    final response = await http.post(Uri.parse('${_baseUrl}api/jobs/$jobId/cancel'));
    if (response.statusCode != 200) {
      throw Exception('Failed to cancel job: ${response.statusCode}');
    }
  }

  Future<List<FileInfo>> getFiles() async {
    final response = await http.get(Uri.parse('${_baseUrl}api/files'));
    if (response.statusCode == 200) {
      final List<dynamic> filesJson = json.decode(response.body);
      return filesJson.map((json) => FileInfo.fromJson(json)).toList();
    }
    throw Exception('Failed to load files: ${response.statusCode}');
  }

  Future<void> deleteFile(String filename) async {
    final response = await http.delete(
      Uri.parse('${_baseUrl}api/files/$filename'),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to delete file: ${response.statusCode}');
    }
  }
}
