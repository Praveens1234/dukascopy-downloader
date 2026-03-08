import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';

class ConnectionScreen extends StatefulWidget {
  const ConnectionScreen({super.key});

  @override
  State<ConnectionScreen> createState() => _ConnectionScreenState();
}

class _ConnectionScreenState extends State<ConnectionScreen>
    with SingleTickerProviderStateMixin {
  final _urlController = TextEditingController();
  late AnimationController _animController;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnim = CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOut,
    );
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animController,
      curve: Curves.easeOutCubic,
    ));
    _animController.forward();

    final provider = context.read<ServerProvider>();
    if (provider.serverUrl.isNotEmpty) {
      _urlController.text =
          provider.serverUrl.replaceFirst('http://', '');
    } else {
      _urlController.text = '192.168.1.100:8000';
    }
  }

  @override
  void dispose() {
    _urlController.dispose();
    _animController.dispose();
    super.dispose();
  }

  Future<void> _connect() async {
    final provider = context.read<ServerProvider>();
    final url = _urlController.text.trim();
    if (url.isEmpty) return;

    final connected = await provider.connect(url);
    if (mounted && connected) {
      Navigator.of(context).pushReplacementNamed('/home');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: FadeTransition(
              opacity: _fadeAnim,
              child: SlideTransition(
                position: _slideAnim,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Logo
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            theme.colorScheme.primary,
                            theme.colorScheme.tertiary,
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color:
                                theme.colorScheme.primary.withValues(alpha: 0.3),
                            blurRadius: 20,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.candlestick_chart_rounded,
                        size: 40,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Title
                    Text(
                      'Dukascopy\nDownloader',
                      textAlign: TextAlign.center,
                      style: GoogleFonts.inter(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        height: 1.2,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Historical Forex Data at Your Fingertips',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                      ),
                    ),
                    const SizedBox(height: 48),

                    // Server URL Input Card
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  Icons.dns_rounded,
                                  size: 20,
                                  color: theme.colorScheme.primary,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Connect to Server',
                                  style: GoogleFonts.inter(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            TextField(
                              controller: _urlController,
                              decoration: InputDecoration(
                                labelText: 'Server Address',
                                hintText: '192.168.1.100:8000',
                                prefixIcon:
                                    const Icon(Icons.link_rounded, size: 20),
                                suffixIcon: provider.isConnected
                                    ? Icon(Icons.check_circle_rounded,
                                        color: theme.colorScheme.primary)
                                    : null,
                              ),
                              keyboardType: TextInputType.url,
                              onSubmitted: (_) => _connect(),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Enter the IP address and port of your PC running the server',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.onSurface
                                    .withValues(alpha: 0.5),
                              ),
                            ),
                            if (provider.connectionError != null) ...[
                              const SizedBox(height: 12),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: theme.colorScheme.error
                                      .withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(
                                    color: theme.colorScheme.error
                                        .withValues(alpha: 0.3),
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Icon(Icons.error_outline_rounded,
                                        size: 18,
                                        color: theme.colorScheme.error),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        provider.connectionError!,
                                        style: TextStyle(
                                          fontSize: 13,
                                          color: theme.colorScheme.error,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                            const SizedBox(height: 20),
                            SizedBox(
                              width: double.infinity,
                              child: FilledButton.icon(
                                onPressed:
                                    provider.isConnecting ? null : _connect,
                                icon: provider.isConnecting
                                    ? SizedBox(
                                        width: 18,
                                        height: 18,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color:
                                              theme.colorScheme.onPrimary,
                                        ),
                                      )
                                    : const Icon(Icons.power_rounded),
                                label: Text(
                                  provider.isConnecting
                                      ? 'Connecting...'
                                      : 'Connect',
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Tips card
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.tips_and_updates_rounded,
                                    size: 18,
                                    color: theme.colorScheme.tertiary),
                                const SizedBox(width: 8),
                                Text(
                                  'Quick Tips',
                                  style: GoogleFonts.inter(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            _tipRow(
                                Icons.computer_rounded,
                                'Start the server on your PC first',
                                theme),
                            const SizedBox(height: 8),
                            _tipRow(
                                Icons.wifi_rounded,
                                'Both devices must be on the same WiFi',
                                theme),
                            const SizedBox(height: 8),
                            _tipRow(
                                Icons.terminal_rounded,
                                'Server shows its IP address on startup',
                                theme),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _tipRow(IconData icon, String text, ThemeData theme) {
    return Row(
      children: [
        Icon(icon,
            size: 16,
            color: theme.colorScheme.onSurface.withValues(alpha: 0.5)),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            text,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
            ),
          ),
        ),
      ],
    );
  }
}
