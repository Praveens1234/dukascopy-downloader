import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/server_config.dart';
import '../models/download_job.dart';
import '../models/download_file.dart';
import '../services/api_service.dart';
import '../services/websocket_service.dart';

class ServerProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final WebSocketService _ws = WebSocketService();

  // Connection state
  bool _isConnected = false;
  bool _isConnecting = false;
  String _serverUrl = '';
  String? _connectionError;

  // Config
  ServerConfig? _config;

  // Jobs
  List<DownloadJob> _jobs = [];
  bool _isLoadingJobs = false;
  Map<String, List<String>> _jobLogs = {};

  // Files
  List<DownloadFile> _files = [];
  bool _isLoadingFiles = false;

  // Download state
  bool _isStartingDownload = false;

  // Theme
  bool _isDarkMode = true;

  // Getters
  bool get isConnected => _isConnected;
  bool get isConnecting => _isConnecting;
  String get serverUrl => _serverUrl;
  String? get connectionError => _connectionError;
  ServerConfig? get config => _config;
  List<DownloadJob> get jobs => _jobs;
  bool get isLoadingJobs => _isLoadingJobs;
  List<DownloadFile> get files => _files;
  bool get isLoadingFiles => _isLoadingFiles;
  bool get isStartingDownload => _isStartingDownload;
  bool get isDarkMode => _isDarkMode;
  WebSocketService get webSocket => _ws;
  ApiService get api => _api;

  StreamSubscription<WebSocketMessage>? _wsSubscription;

  ServerProvider() {
    _loadSavedSettings();
  }

  Future<void> _loadSavedSettings() async {
    final prefs = await SharedPreferences.getInstance();
    _serverUrl = prefs.getString('server_url') ?? '';
    _isDarkMode = prefs.getBool('dark_mode') ?? true;
    notifyListeners();

    if (_serverUrl.isNotEmpty) {
      await connect(_serverUrl);
    }
  }

  Future<bool> connect(String url) async {
    _isConnecting = true;
    _connectionError = null;
    notifyListeners();

    final cleanUrl = url.endsWith('/') ? url.substring(0, url.length - 1) : url;
    if (!cleanUrl.startsWith('http')) {
      _api.updateBaseUrl('http://$cleanUrl');
    } else {
      _api.updateBaseUrl(cleanUrl);
    }

    try {
      final connected = await _api.testConnection();
      if (connected) {
        _serverUrl = _api.baseUrl;
        _isConnected = true;
        _connectionError = null;

        // Save URL
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('server_url', _serverUrl);

        // Load config
        _config = await _api.getConfig();

        // Connect WebSocket
        _connectWebSocket();

        // Load initial data
        await Future.wait([loadJobs(), loadFiles()]);
      } else {
        _isConnected = false;
        _connectionError = 'Server not responding';
      }
    } catch (e) {
      _isConnected = false;
      _connectionError = e.toString();
    }

    _isConnecting = false;
    notifyListeners();
    return _isConnected;
  }

  void _connectWebSocket() {
    _wsSubscription?.cancel();
    _ws.connect(_serverUrl);
    _wsSubscription = _ws.messages.listen(_handleWebSocketMessage);
  }

  void _handleWebSocketMessage(WebSocketMessage msg) {
    switch (msg.type) {
      case 'log':
        if (msg.jobId != null && msg.message != null) {
          _jobLogs[msg.jobId!] ??= [];
          _jobLogs[msg.jobId!]!.add(msg.message!);
          // Keep only last 500 lines
          if (_jobLogs[msg.jobId!]!.length > 500) {
            _jobLogs[msg.jobId!] = _jobLogs[msg.jobId!]!.sublist(
                _jobLogs[msg.jobId!]!.length - 500);
          }
          notifyListeners();
        }
        break;
      case 'progress':
        if (msg.jobId != null) {
          final idx = _jobs.indexWhere((j) => j.id == msg.jobId);
          if (idx >= 0) {
            _jobs[idx] = _jobs[idx].copyWith(
              status: msg.status,
              progress: msg.progress,
              completedDays: msg.completedDays,
              totalDays: msg.totalDays,
            );
            notifyListeners();
          }
        }
        break;
      case 'full_logs':
        if (msg.jobId != null && msg.logs != null) {
          _jobLogs[msg.jobId!] = msg.logs!;
          notifyListeners();
        }
        break;
    }
  }

  List<String> getJobLogs(String jobId) {
    return _jobLogs[jobId] ?? [];
  }

  void requestJobLogs(String jobId) {
    _ws.requestLogs(jobId);
  }

  Future<void> loadJobs() async {
    if (!_isConnected) return;
    _isLoadingJobs = true;
    notifyListeners();

    try {
      _jobs = await _api.getJobs();
    } catch (_) {}

    _isLoadingJobs = false;
    notifyListeners();
  }

  Future<void> loadFiles() async {
    if (!_isConnected) return;
    _isLoadingFiles = true;
    notifyListeners();

    try {
      _files = await _api.getFiles();
    } catch (_) {}

    _isLoadingFiles = false;
    notifyListeners();
  }

  Future<String?> startDownload({
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
    _isStartingDownload = true;
    notifyListeners();

    try {
      final jobId = await _api.startDownload(
        symbols: symbols,
        startDate: startDate,
        endDate: endDate,
        timeframe: timeframe,
        threads: threads,
        dataSource: dataSource,
        priceType: priceType,
        volumeType: volumeType,
        customTf: customTf,
      );

      // Refresh jobs list
      await loadJobs();

      _isStartingDownload = false;
      notifyListeners();
      return jobId;
    } catch (e) {
      _isStartingDownload = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<bool> cancelJob(String jobId) async {
    try {
      final success = await _api.cancelJob(jobId);
      if (success) {
        await loadJobs();
      }
      return success;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteFile(String filename) async {
    try {
      final success = await _api.deleteFile(filename);
      if (success) {
        await loadFiles();
      }
      return success;
    } catch (_) {
      return false;
    }
  }

  void toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('dark_mode', _isDarkMode);
    notifyListeners();
  }

  void disconnect() {
    _wsSubscription?.cancel();
    _ws.disconnect();
    _isConnected = false;
    _config = null;
    _jobs = [];
    _files = [];
    _jobLogs = {};
    notifyListeners();
  }

  @override
  void dispose() {
    _wsSubscription?.cancel();
    _ws.dispose();
    super.dispose();
  }
}
