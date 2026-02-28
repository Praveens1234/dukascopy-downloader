import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/job.dart';
import '../models/download_request.dart';

class ApiService {
  Future<String> get _baseUrl async {
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString('server_url');
    if (url == null || url.isEmpty) {
      throw Exception('Server URL not set. Please connect first.');
    }
    return url;
  }

  Future<String?> getBaseUrl() async {
     final prefs = await SharedPreferences.getInstance();
     return prefs.getString('server_url');
  }

  Future<void> setBaseUrl(String url) async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('server_url', url);
  }

  Future<Map<String, dynamic>> checkConnection(String url) async {
    final res = await http.get(Uri.parse('$url/api/status')).timeout(const Duration(seconds: 5));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to connect: ${res.statusCode}');
  }

  Future<Map<String, dynamic>> getConfig() async {
    final url = await _baseUrl;
    final res = await http.get(Uri.parse('$url/api/config'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load config');
  }

  Future<List<Job>> getJobs() async {
    final url = await _baseUrl;
    final res = await http.get(Uri.parse('$url/api/jobs'));
    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.map((j) => Job.fromJson(j)).toList();
    }
    throw Exception('Failed to load jobs');
  }

  Future<Job> getJob(String id) async {
    final url = await _baseUrl;
    final res = await http.get(Uri.parse('$url/api/jobs/$id'));
    if (res.statusCode == 200) {
      return Job.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to load job');
  }

  Future<Job> startDownload(DownloadRequest req) async {
    final url = await _baseUrl;
    final res = await http.post(
      Uri.parse('$url/api/jobs'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(req.toJson()),
    );
    if (res.statusCode == 200 || res.statusCode == 201) {
      return Job.fromJson(jsonDecode(res.body));
    }
    throw Exception('Failed to start download: ${res.body}');
  }

  Future<void> cancelJob(String id) async {
    final url = await _baseUrl;
    final res = await http.post(Uri.parse('$url/api/jobs/$id/cancel'));
    if (res.statusCode != 200) {
      throw Exception('Failed to cancel job: ${res.body}');
    }
  }

  Future<void> deleteJob(String id) async {
    final url = await _baseUrl;
    final res = await http.delete(Uri.parse('$url/api/jobs/$id'));
    if (res.statusCode != 200) {
      throw Exception('Failed to delete job: ${res.body}');
    }
  }

  Future<List<String>> listFiles() async {
    final url = await _baseUrl;
    final res = await http.get(Uri.parse('$url/api/files'));
    if (res.statusCode == 200) {
      final List<dynamic> data = jsonDecode(res.body);
      return data.cast<String>();
    }
    throw Exception('Failed to load files');
  }

  Future<void> deleteFile(String filename) async {
    final url = await _baseUrl;
    final res = await http.delete(Uri.parse('$url/api/files/$filename'));
    if (res.statusCode != 200) {
      throw Exception('Failed to delete file: ${res.body}');
    }
  }
}
