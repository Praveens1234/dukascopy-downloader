import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'home_screen.dart';

class ConnectionScreen extends StatefulWidget {
  final String? errorMsg;
  const ConnectionScreen({super.key, this.errorMsg});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen> {
  final TextEditingController _urlController = TextEditingController();
  bool _isLoading = false;
  String? _errorMsg;

  @override
  void initState() {
    super.initState();
    _errorMsg = widget.errorMsg;
    _loadLastUrl();
  }

  Future<void> _loadLastUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString('server_url');
    if (url != null) {
      _urlController.text = url;
    }
  }

  Future<void> _connect(String url) async {
    if (url.isEmpty) return;

    // Auto-fix missing http://
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://$url';
    }

    setState(() {
      _isLoading = true;
      _errorMsg = null;
    });

    try {
      // Ping the config endpoint to verify connection
      final response = await http.get(Uri.parse('$url/api/config')).timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        // Save successfully connected URL
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('server_url', url);

        if (!mounted) return;
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => HomeScreen(serverUrl: url)),
        );
      } else {
        setState(() {
          _errorMsg = 'Server returned error: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _errorMsg = 'Failed to connect. Check IP and Port.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _scanQRCode() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(title: const Text('Scan QR Code')),
          body: MobileScanner(
            onDetect: (capture) {
              final List<Barcode> barcodes = capture.barcodes;
              for (final barcode in barcodes) {
                if (barcode.rawValue != null && barcode.rawValue!.startsWith('http')) {
                  Navigator.pop(context);
                  _urlController.text = barcode.rawValue!;
                  _connect(barcode.rawValue!);
                  break;
                }
              }
            },
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.download_rounded, size: 80, color: Color(0xFF3B82F6)),
              const SizedBox(height: 24),
              const Text(
                'Connect to Server',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Enter the IP address shown on your PC or scan the QR code.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 40),

              if (_errorMsg != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    border: Border.all(color: Colors.red.withOpacity(0.5)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _errorMsg!,
                    style: const TextStyle(color: Colors.redAccent),
                  ),
                ),

              TextField(
                controller: _urlController,
                decoration: const InputDecoration(
                  labelText: 'Server URL (e.g., http://192.168.1.5:8000)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.link),
                ),
                keyboardType: TextInputType.url,
                onSubmitted: _connect,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: _isLoading ? null : () => _connect(_urlController.text),
                icon: _isLoading
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.arrow_forward),
                label: Text(_isLoading ? 'Connecting...' : 'Connect'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.all(16),
                  backgroundColor: const Color(0xFF3B82F6),
                  foregroundColor: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: _isLoading ? null : _scanQRCode,
                icon: const Icon(Icons.qr_code_scanner),
                label: const Text('Scan QR Code'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.all(16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
