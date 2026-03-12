import 'package:flutter/foundation.dart';

class ServerConfigService extends ChangeNotifier {
  String _serverUrl = 'http://192.168.1.100:8000';
  bool _isConnected = false;
  String? _connectionError;

  String get serverUrl => _serverUrl;
  bool get isConnected => _isConnected;
  String? get connectionError => _connectionError;

  void setServerUrl(String url) {
    _serverUrl = url;
    notifyListeners();
  }

  void setConnectionStatus(bool connected, {String? error}) {
    _isConnected = connected;
    _connectionError = error;
    notifyListeners();
  }

  Future<bool> testConnection() async {
    try {
      // Simple connection test will be done by API service
      _isConnected = true;
      notifyListeners();
      return true;
    } catch (e) {
      _isConnected = false;
      _connectionError = e.toString();
      notifyListeners();
      return false;
    }
  }
}
