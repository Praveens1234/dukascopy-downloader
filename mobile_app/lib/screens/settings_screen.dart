import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Connection Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.dns_rounded,
                          size: 20, color: theme.colorScheme.primary),
                      const SizedBox(width: 10),
                      Text('Server Connection',
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          )),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildInfoRow(theme, 'Status',
                      provider.isConnected ? 'Connected' : 'Disconnected',
                      valueColor: provider.isConnected
                          ? const Color(0xFF10B981)
                          : theme.colorScheme.error),
                  const SizedBox(height: 10),
                  _buildInfoRow(
                      theme, 'Server URL', provider.serverUrl.isEmpty
                          ? 'Not configured'
                          : provider.serverUrl),
                  if (provider.config != null) ...[
                    const SizedBox(height: 10),
                    _buildInfoRow(theme, 'Symbols Available',
                        '${provider.config!.symbols.length}'),
                    const SizedBox(height: 10),
                    _buildInfoRow(theme, 'Max Threads',
                        '${provider.config!.maxThreads}'),
                  ],
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            provider.disconnect();
                            Navigator.of(context).pushReplacementNamed('/');
                          },
                          icon: const Icon(Icons.link_off_rounded, size: 18),
                          label: const Text('Disconnect'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: () async {
                            await provider.connect(provider.serverUrl);
                          },
                          icon: const Icon(Icons.refresh_rounded, size: 18),
                          label: const Text('Reconnect'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Appearance Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.palette_rounded,
                          size: 20, color: theme.colorScheme.tertiary),
                      const SizedBox(width: 10),
                      Text('Appearance',
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          )),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildSwitchRow(
                    theme,
                    'Dark Mode',
                    Icons.dark_mode_rounded,
                    provider.isDarkMode,
                    (_) => provider.toggleTheme(),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // About Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline_rounded,
                          size: 20, color: theme.colorScheme.secondary),
                      const SizedBox(width: 10),
                      Text('About',
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                          )),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildInfoRow(theme, 'App', 'Dukascopy Downloader'),
                  const SizedBox(height: 10),
                  _buildInfoRow(theme, 'Version', '1.0.0'),
                  const SizedBox(height: 10),
                  _buildInfoRow(theme, 'Platform', 'Flutter / Material You'),
                  const SizedBox(height: 10),
                  _buildInfoRow(
                      theme, 'Description',
                      'Download historical forex data from Dukascopy. '
                          'Supports tick and candle data with multiple '
                          'timeframes.'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Version footer
          Center(
            child: Text(
              'Dukascopy Downloader v1.0.0',
              style: TextStyle(
                fontSize: 12,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.3),
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildInfoRow(ThemeData theme, String label, String value,
      {Color? valueColor}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 120,
          child: Text(label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
              )),
        ),
        Expanded(
          child: Text(value,
              style: GoogleFonts.inter(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: valueColor ?? theme.colorScheme.onSurface,
              )),
        ),
      ],
    );
  }

  Widget _buildSwitchRow(ThemeData theme, String label, IconData icon,
      bool value, ValueChanged<bool> onChanged) {
    return Row(
      children: [
        Icon(icon,
            size: 20,
            color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
        const SizedBox(width: 12),
        Expanded(
          child: Text(label,
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              )),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
        ),
      ],
    );
  }
}
