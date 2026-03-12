import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService extends ChangeNotifier {
  WebSocketChannel? _channel;
  bool _isConnected = false;
  final List<String> _logs = [];
  final Map<String, dynamic> _latestProgress = {};

  bool get isConnected => _isConnected;
  List<String> get logs => _logs;
  Map<String, dynamic> get latestProgress => _latestProgress;

  void connect(String wsUrl) {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _isConnected = true;
      notifyListeners();

      _channel!.stream.listen(
        (message) {
          try {
            final data = json.decode(message);
            if (data['type'] == 'log') {
              _logs.add('${data['message']}');
              if (_logs.length > 500) _logs.removeAt(0);
            } else if (data['type'] == 'progress') {
              _latestProgress = data;
            }
            notifyListeners();
          } catch (e) {
            debugPrint('WebSocket message parse error: $e');
          }
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          debugPrint('WebSocket connection closed');
          _isConnected = false;
          notifyListeners();
        },
      );
    } catch (e) {
      debugPrint('WebSocket connect error: $e');
      _isConnected = false;
      notifyListeners();
    }
  }

  void disconnect() {
    _channel?.close();
    _channel = null;
    _isConnected = false;
    _logs.clear();
    _latestProgress.clear();
    notifyListeners();
  }

  void getLogs(String jobId) {
    if (_channel != null && _isConnected) {
      _channel!.sink.add(json.encode({
        'type': 'get_logs',
        'job_id': jobId,
      }));
    }
  }
}
