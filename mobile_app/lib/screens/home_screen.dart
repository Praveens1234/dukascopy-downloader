import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'connection_screen.dart';
import 'new_download_tab.dart';
import 'jobs_tab.dart';
import 'files_tab.dart';
import 'terminal_tab.dart';

class HomeScreen extends StatefulWidget {
  final String serverUrl;

  const HomeScreen({super.key, required this.serverUrl});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  WebSocketChannel? _channel;
  bool _wsConnected = false;
  Map<String, dynamic> _config = {};
  String? _activeJobId;

  // Shared state for tabs
  List<dynamic> _jobs = [];
  List<dynamic> _files = [];
  List<String> _logs = [];
  Map<String, dynamic>? _activeJobProgress;

  @override
  void initState() {
    super.initState();
    _fetchConfig();
    _connectWebSocket();
    _pollJobs();
    _pollFiles();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  void _disconnect() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('server_url');
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const ConnectionScreen()),
    );
  }

  Future<void> _fetchConfig() async {
    try {
      final res = await http.get(Uri.parse('${widget.serverUrl}/api/config'));
      if (res.statusCode == 200) {
        setState(() {
          _config = jsonDecode(res.body);
        });
      }
    } catch (e) {
      debugPrint("Error fetching config: $e");
    }
  }

  void _connectWebSocket() {
    final wsUrl = widget.serverUrl.replaceAll('http://', 'ws://').replaceAll('https://', 'wss://');
    try {
      _channel = WebSocketChannel.connect(Uri.parse('$wsUrl/ws'));
      setState(() => _wsConnected = true);

      _channel!.stream.listen((message) {
        final data = jsonDecode(message);
        if (data['type'] == 'log') {
          setState(() {
            _logs.add(data['message']);
            if (_logs.length > 500) _logs.removeAt(0);
          });
        } else if (data['type'] == 'full_logs') {
          setState(() {
            _logs = List<String>.from(data['logs']);
          });
        } else if (data['type'] == 'progress') {
          setState(() {
            _activeJobProgress = data;
            if (data['status'] == 'completed' || data['status'] == 'failed' || data['status'] == 'cancelled') {
              _pollJobs();
              _pollFiles();
            }
          });
        }
      }, onDone: () {
        setState(() => _wsConnected = false);
        Future.delayed(const Duration(seconds: 3), _connectWebSocket);
      }, onError: (err) {
        setState(() => _wsConnected = false);
      });
    } catch (e) {
      setState(() => _wsConnected = false);
    }
  }

  Future<void> _pollJobs() async {
    try {
      final res = await http.get(Uri.parse('${widget.serverUrl}/api/jobs'));
      if (res.statusCode == 200) {
        setState(() {
          _jobs = jsonDecode(res.body);
        });
      }
    } catch (e) {
      debugPrint("Error fetching jobs: $e");
    }
  }

  Future<void> _pollFiles() async {
    try {
      final res = await http.get(Uri.parse('${widget.serverUrl}/api/files'));
      if (res.statusCode == 200) {
        setState(() {
          _files = jsonDecode(res.body);
        });
      }
    } catch (e) {
      debugPrint("Error fetching files: $e");
    }
  }

  void _startJob(String jobId) {
    setState(() {
      _activeJobId = jobId;
      _activeJobProgress = null;
      _logs.clear();
      _currentIndex = 3; // Switch to terminal
    });
    // Request logs for the new job
    if (_wsConnected) {
      _channel?.sink.add(jsonEncode({'type': 'get_logs', 'job_id': jobId}));
    }
    _pollJobs();
  }

  void _viewJobLogs(String jobId) {
    setState(() {
      _activeJobId = jobId;
      _logs.clear();
      _currentIndex = 3; // Switch to terminal tab
    });
    if (_wsConnected) {
      _channel?.sink.add(jsonEncode({'type': 'get_logs', 'job_id': jobId}));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dukascopy Downloader'),
        actions: [
          Icon(
            _wsConnected ? Icons.wifi : Icons.wifi_off,
            color: _wsConnected ? Colors.greenAccent : Colors.redAccent,
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _disconnect,
            tooltip: 'Disconnect',
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          NewDownloadTab(
            serverUrl: widget.serverUrl,
            config: _config,
            onJobStarted: _startJob,
          ),
          JobsTab(
            serverUrl: widget.serverUrl,
            jobs: _jobs,
            onRefresh: _pollJobs,
            onViewLogs: _viewJobLogs,
          ),
          FilesTab(
            serverUrl: widget.serverUrl,
            files: _files,
            onRefresh: _pollFiles,
          ),
          TerminalTab(
            logs: _logs,
            activeJobProgress: _activeJobProgress,
            onClear: () => setState(() => _logs.clear()),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
            if (index == 1) _pollJobs();
            if (index == 2) _pollFiles();
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.download),
            label: 'Download',
          ),
          NavigationDestination(
            icon: Icon(Icons.list_alt),
            label: 'Jobs',
          ),
          NavigationDestination(
            icon: Icon(Icons.folder),
            label: 'Files',
          ),
          NavigationDestination(
            icon: Icon(Icons.terminal),
            label: 'Terminal',
          ),
        ],
      ),
    );
  }
}
