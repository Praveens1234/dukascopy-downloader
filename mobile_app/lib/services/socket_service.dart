import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SocketService {
  WebSocketChannel? _channel;
  final StreamController<dynamic> _controller = StreamController.broadcast();
  Stream<dynamic> get stream => _controller.stream;

  Future<void> connect() async {
    final prefs = await SharedPreferences.getInstance();
    final baseUrl = prefs.getString('base_url');
    if (baseUrl == null) return;

    // Convert http:// to ws://
    String wsUrl = baseUrl.replaceFirst('http', 'ws');
    if (wsUrl.endsWith('/')) wsUrl = wsUrl.substring(0, wsUrl.length - 1);
    wsUrl += '/ws';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _channel!.stream.listen(
        (message) {
          _controller.add(json.decode(message));
        },
        onError: (error) {
          print("WS Error: $error");
          _controller.addError(error);
        },
        onDone: () {
          print("WS Closed");
        },
      );
    } catch (e) {
      print("WS Connect Error: $e");
    }
  }

  void subscribeToJob(String jobId) {
    if (_channel != null) {
      _channel!.sink.add(json.encode({'type': 'get_logs', 'job_id': jobId}));
    }
  }

  void close() {
    _channel?.sink.close();
    // Do not close controller here as it might be reused or we might want to keep listening
  }

  void dispose() {
    _channel?.sink.close();
    _controller.close();
  }
}
