import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketMessage {
  final String type;
  final String? jobId;
  final String? message;
  final String? status;
  final double? progress;
  final int? completedDays;
  final int? totalDays;
  final List<String>? logs;

  WebSocketMessage({
    required this.type,
    this.jobId,
    this.message,
    this.status,
    this.progress,
    this.completedDays,
    this.totalDays,
    this.logs,
  });

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] ?? '',
      jobId: json['job_id'],
      message: json['message'],
      status: json['status'],
      progress: json['progress']?.toDouble(),
      completedDays: json['completed_days'],
      totalDays: json['total_days'],
      logs: json['logs'] != null ? List<String>.from(json['logs']) : null,
    );
  }
}

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<WebSocketMessage> _messageController =
      StreamController<WebSocketMessage>.broadcast();
  bool _isConnected = false;
  Timer? _reconnectTimer;
  String _wsUrl = '';

  Stream<WebSocketMessage> get messages => _messageController.stream;
  bool get isConnected => _isConnected;

  void connect(String baseUrl) {
    disconnect();
    final wsScheme = baseUrl.startsWith('https') ? 'wss' : 'ws';
    final host = baseUrl.replaceFirst(RegExp(r'https?://'), '');
    _wsUrl = '$wsScheme://$host/ws';

    _doConnect();
  }

  void _doConnect() {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(_wsUrl));
      _isConnected = true;

      _channel!.stream.listen(
        (data) {
          try {
            final json = jsonDecode(data as String) as Map<String, dynamic>;
            final msg = WebSocketMessage.fromJson(json);
            _messageController.add(msg);
          } catch (_) {}
        },
        onError: (error) {
          _isConnected = false;
          _scheduleReconnect();
        },
        onDone: () {
          _isConnected = false;
          _scheduleReconnect();
        },
      );
    } catch (e) {
      _isConnected = false;
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      if (!_isConnected && _wsUrl.isNotEmpty) {
        _doConnect();
      }
    });
  }

  void requestLogs(String jobId) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(jsonEncode({'type': 'get_logs', 'job_id': jobId}));
    }
  }

  void disconnect() {
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
