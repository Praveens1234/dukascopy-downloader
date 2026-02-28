import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/job.dart';
import '../models/download_request.dart';

class ApiService {
  String? _baseUrl;
  static const String _baseUrlKey = 'base_url';

  // Get current base URL or load from prefs
  Future<String?> getBaseUrl() async {
    if (_baseUrl != null) return _baseUrl;
    final prefs = await SharedPreferences.getInstance();
    _baseUrl = prefs.getString(_baseUrlKey);
    return _baseUrl;
  }

  // Set new base URL and save to prefs
  Future<void> setBaseUrl(String url) async {
    // Ensure no trailing slash
    if (url.endsWith('/')) {
      url = url.substring(0, url.length - 1);
    }
    _baseUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_baseUrlKey, url);
  }

  // Generic GET helper
  Future<dynamic> _get(String endpoint) async {
    final baseUrl = await getBaseUrl();
    if (baseUrl == null) throw Exception("Server URL not configured");

    try {
      final response = await http.get(Uri.parse('$baseUrl$endpoint'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection failed: $e');
    }
  }

  // Generic POST helper
  Future<dynamic> _post(String endpoint, [Map<String, dynamic>? body]) async {
    final baseUrl = await getBaseUrl();
    if (baseUrl == null) throw Exception("Server URL not configured");

    try {
      final response = await http.post(
        Uri.parse('$baseUrl$endpoint'),
        headers: {'Content-Type': 'application/json'},
        body: body != null ? json.encode(body) : null,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection failed: $e');
    }
  }

  // --- API Methods ---

  Future<List<Job>> getJobs() async {
    final List<dynamic> data = await _get('/api/jobs');
    return data.map((j) => Job.fromJson(j)).toList();
  }

  Future<Job> getJob(String id) async {
    final data = await _get('/api/jobs/$id');
    return Job.fromJson(data);
  }

  Future<Map<String, dynamic>> getConfig() async {
    return await _get('/api/config');
  }

  Future<String> startDownload(DownloadRequest request) async {
    final data = await _post('/api/download', request.toJson());
    return data['job_id'];
  }

  Future<bool> cancelJob(String jobId) async {
    try {
      await _post('/api/jobs/$jobId/cancel');
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> getFiles() async {
    final List<dynamic> data = await _get('/api/files');
    return List<Map<String, dynamic>>.from(data);
  }

  Future<void> deleteFile(String filename) async {
    final baseUrl = await getBaseUrl();
    if (baseUrl == null) throw Exception("Server URL not configured");

    final response = await http.delete(Uri.parse('$baseUrl/api/files/$filename'));
    if (response.statusCode != 200) {
      throw Exception('Failed to delete file');
    }
  }
}
