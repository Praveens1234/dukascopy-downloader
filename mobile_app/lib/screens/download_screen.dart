import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';

class DownloadScreen extends StatefulWidget {
  const DownloadScreen({super.key});

  @override
  State<DownloadScreen> createState() => _DownloadScreenState();
}

class _DownloadScreenState extends State<DownloadScreen>
    with AutomaticKeepAliveClientMixin {
  final Set<String> _selectedSymbols = {};
  final _customSymbolController = TextEditingController();
  final Set<String> _customSymbols = {};

  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now().subtract(const Duration(days: 1));

  String _timeframe = 'M1';
  int _threads = 5;
  String _dataSource = 'auto';
  String _priceType = 'BID';
  String _volumeType = 'TOTAL';
  String _customTf = '';
  bool _showAdvanced = false;

  @override
  bool get wantKeepAlive => true;

  @override
  void dispose() {
    _customSymbolController.dispose();
    super.dispose();
  }

  Future<void> _pickDate(bool isStart) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: isStart ? _startDate : _endDate,
      firstDate: DateTime(2003),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            datePickerTheme: DatePickerThemeData(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          _startDate = picked;
        } else {
          _endDate = picked;
        }
      });
    }
  }

  void _addCustomSymbol() {
    final symbol = _customSymbolController.text.trim().toUpperCase();
    if (symbol.isNotEmpty && symbol.length >= 3) {
      setState(() {
        _customSymbols.add(symbol);
        _selectedSymbols.add(symbol);
        _customSymbolController.clear();
      });
    }
  }

  Future<void> _startDownload() async {
    if (_selectedSymbols.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select at least one symbol')),
      );
      return;
    }

    final provider = context.read<ServerProvider>();
    final dateFormat = DateFormat('yyyy-MM-dd');

    try {
      final jobId = await provider.startDownload(
        symbols: _selectedSymbols.toList(),
        startDate: dateFormat.format(_startDate),
        endDate: dateFormat.format(_endDate),
        timeframe: _timeframe,
        threads: _threads,
        dataSource: _dataSource,
        priceType: _priceType,
        volumeType: _volumeType,
        customTf: _timeframe == 'CUSTOM' ? _customTf : null,
      );

      if (mounted && jobId != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle_rounded,
                    color: Theme.of(context).colorScheme.primary, size: 20),
                const SizedBox(width: 8),
                Text('Download started! Job: $jobId'),
              ],
            ),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();
    final config = provider.config;

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Download'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () async {
              await provider.connect(provider.serverUrl);
            },
            tooltip: 'Refresh config',
          ),
        ],
      ),
      body: config == null
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Symbol Selection Card
                  _buildSectionCard(
                    theme: theme,
                    icon: Icons.currency_exchange_rounded,
                    title: 'Symbols',
                    subtitle:
                        '${_selectedSymbols.length} selected',
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Quick actions
                        Row(
                          children: [
                            _buildMiniButton(
                              theme,
                              'Select All',
                              Icons.select_all_rounded,
                              () => setState(() => _selectedSymbols
                                  .addAll(config.symbols)),
                            ),
                            const SizedBox(width: 8),
                            _buildMiniButton(
                              theme,
                              'Clear',
                              Icons.clear_all_rounded,
                              () => setState(() {
                                _selectedSymbols.clear();
                                _selectedSymbols.addAll(_customSymbols);
                              }),
                            ),
                            const SizedBox(width: 8),
                            _buildMiniButton(
                              theme,
                              'Majors',
                              Icons.star_rounded,
                              () => setState(() {
                                _selectedSymbols.addAll([
                                  'EURUSD',
                                  'GBPUSD',
                                  'USDJPY',
                                  'USDCHF',
                                  'AUDUSD',
                                  'USDCAD',
                                  'NZDUSD'
                                ]);
                              }),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Symbol chips
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: [
                            ...config.symbols.map((symbol) {
                              final isSelected =
                                  _selectedSymbols.contains(symbol);
                              return FilterChip(
                                label: Text(symbol,
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w500,
                                      color: isSelected
                                          ? theme.colorScheme.onPrimary
                                          : theme.colorScheme.onSurface
                                              .withValues(alpha: 0.8),
                                    )),
                                selected: isSelected,
                                onSelected: (selected) {
                                  setState(() {
                                    if (selected) {
                                      _selectedSymbols.add(symbol);
                                    } else {
                                      _selectedSymbols.remove(symbol);
                                    }
                                  });
                                },
                                selectedColor: theme.colorScheme.primary,
                                checkmarkColor:
                                    theme.colorScheme.onPrimary,
                                showCheckmark: false,
                                visualDensity: VisualDensity.compact,
                              );
                            }),
                            ..._customSymbols.map((symbol) {
                              return InputChip(
                                label: Text(symbol,
                                    style: const TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.w500,
                                      color: Colors.white,
                                    )),
                                backgroundColor:
                                    theme.colorScheme.tertiary,
                                deleteIconColor:
                                    Colors.white.withValues(alpha: 0.7),
                                onDeleted: () {
                                  setState(() {
                                    _customSymbols.remove(symbol);
                                    _selectedSymbols.remove(symbol);
                                  });
                                },
                                visualDensity: VisualDensity.compact,
                              );
                            }),
                          ],
                        ),
                        const SizedBox(height: 12),
                        // Custom symbol input
                        Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _customSymbolController,
                                decoration: InputDecoration(
                                  hintText: 'Custom symbol (e.g. BTCUSD)',
                                  isDense: true,
                                  contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 10),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                ),
                                textCapitalization:
                                    TextCapitalization.characters,
                                onSubmitted: (_) => _addCustomSymbol(),
                              ),
                            ),
                            const SizedBox(width: 8),
                            IconButton.filled(
                              onPressed: _addCustomSymbol,
                              icon: const Icon(Icons.add_rounded, size: 20),
                              style: IconButton.styleFrom(
                                minimumSize: const Size(42, 42),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Date Range Card
                  _buildSectionCard(
                    theme: theme,
                    icon: Icons.date_range_rounded,
                    title: 'Date Range',
                    child: Row(
                      children: [
                        Expanded(
                          child: _buildDateButton(
                            theme,
                            'Start',
                            _startDate,
                            () => _pickDate(true),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          child: Icon(Icons.arrow_forward_rounded,
                              size: 20,
                              color: theme.colorScheme.onSurface
                                  .withValues(alpha: 0.4)),
                        ),
                        Expanded(
                          child: _buildDateButton(
                            theme,
                            'End',
                            _endDate,
                            () => _pickDate(false),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Timeframe Card
                  _buildSectionCard(
                    theme: theme,
                    icon: Icons.timer_rounded,
                    title: 'Timeframe',
                    child: Column(
                      children: [
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: (config.timeframes).map((tf) {
                            final isSelected = _timeframe == tf;
                            return ChoiceChip(
                              label: Text(tf,
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: isSelected
                                        ? theme.colorScheme.onPrimary
                                        : theme.colorScheme.onSurface
                                            .withValues(alpha: 0.7),
                                  )),
                              selected: isSelected,
                              onSelected: (_) =>
                                  setState(() => _timeframe = tf),
                              selectedColor: theme.colorScheme.primary,
                              showCheckmark: false,
                              visualDensity: VisualDensity.compact,
                            );
                          }).toList(),
                        ),
                        if (_timeframe == 'CUSTOM') ...[
                          const SizedBox(height: 12),
                          TextField(
                            decoration: InputDecoration(
                              hintText:
                                  'Custom timeframe (e.g. 120, 5m, 2h)',
                              isDense: true,
                              contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 10),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                            onChanged: (v) => _customTf = v,
                          ),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Advanced Options
                  Card(
                    child: Column(
                      children: [
                        InkWell(
                          onTap: () =>
                              setState(() => _showAdvanced = !_showAdvanced),
                          borderRadius: BorderRadius.circular(16),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              children: [
                                Icon(Icons.tune_rounded,
                                    size: 20,
                                    color: theme.colorScheme.primary),
                                const SizedBox(width: 10),
                                Text('Advanced Options',
                                    style: GoogleFonts.inter(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w600,
                                    )),
                                const Spacer(),
                                AnimatedRotation(
                                  turns: _showAdvanced ? 0.5 : 0,
                                  duration: const Duration(milliseconds: 200),
                                  child: Icon(
                                      Icons.keyboard_arrow_down_rounded,
                                      color: theme.colorScheme.onSurface
                                          .withValues(alpha: 0.5)),
                                ),
                              ],
                            ),
                          ),
                        ),
                        AnimatedCrossFade(
                          firstChild: const SizedBox.shrink(),
                          secondChild: Padding(
                            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                            child: Column(
                              children: [
                                const Divider(),
                                const SizedBox(height: 12),
                                // Threads slider
                                _buildSliderRow(
                                  theme,
                                  'Threads',
                                  Icons.memory_rounded,
                                  _threads.toDouble(),
                                  1,
                                  config.maxThreads.toDouble(),
                                  (v) => setState(
                                      () => _threads = v.round()),
                                ),
                                const SizedBox(height: 16),
                                // Data source
                                _buildDropdownRow(
                                  theme,
                                  'Data Source',
                                  Icons.source_rounded,
                                  _dataSource,
                                  ['auto', 'tick', 'native'],
                                  (v) => setState(() => _dataSource = v!),
                                ),
                                const SizedBox(height: 12),
                                // Price type
                                _buildDropdownRow(
                                  theme,
                                  'Price Type',
                                  Icons.price_change_rounded,
                                  _priceType,
                                  ['BID', 'ASK', 'MID'],
                                  (v) => setState(() => _priceType = v!),
                                ),
                                const SizedBox(height: 12),
                                // Volume type
                                _buildDropdownRow(
                                  theme,
                                  'Volume Type',
                                  Icons.bar_chart_rounded,
                                  _volumeType,
                                  config.volumeTypes,
                                  (v) => setState(() => _volumeType = v!),
                                ),
                              ],
                            ),
                          ),
                          crossFadeState: _showAdvanced
                              ? CrossFadeState.showSecond
                              : CrossFadeState.showFirst,
                          duration: const Duration(milliseconds: 300),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Start Download Button
                  SizedBox(
                    width: double.infinity,
                    height: 54,
                    child: FilledButton.icon(
                      onPressed: provider.isStartingDownload
                          ? null
                          : _startDownload,
                      icon: provider.isStartingDownload
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.rocket_launch_rounded),
                      label: Text(
                        provider.isStartingDownload
                            ? 'Starting...'
                            : 'Start Download',
                        style: GoogleFonts.inter(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      style: FilledButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionCard({
    required ThemeData theme,
    required IconData icon,
    required String title,
    String? subtitle,
    required Widget child,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: theme.colorScheme.primary),
                const SizedBox(width: 10),
                Text(title,
                    style: GoogleFonts.inter(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    )),
                if (subtitle != null) ...[
                  const Spacer(),
                  Text(subtitle,
                      style: TextStyle(
                        fontSize: 12,
                        color:
                            theme.colorScheme.onSurface.withValues(alpha: 0.5),
                      )),
                ],
              ],
            ),
            const SizedBox(height: 14),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildMiniButton(
      ThemeData theme, String label, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          border: Border.all(
              color: theme.colorScheme.outline.withValues(alpha: 0.3)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                size: 14,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            const SizedBox(width: 4),
            Text(label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildDateButton(
      ThemeData theme, String label, DateTime date, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          border: Border.all(
              color: theme.colorScheme.outline.withValues(alpha: 0.3)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                  letterSpacing: 0.5,
                )),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.calendar_today_rounded,
                    size: 16, color: theme.colorScheme.primary),
                const SizedBox(width: 6),
                Text(
                  DateFormat('MMM dd, yyyy').format(date),
                  style: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliderRow(ThemeData theme, String label, IconData icon,
      double value, double min, double max, ValueChanged<double> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon,
                size: 18,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
            const SizedBox(width: 8),
            Text(label,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
                )),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text('${value.round()}',
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: theme.colorScheme.primary,
                  )),
            ),
          ],
        ),
        Slider(
          value: value,
          min: min,
          max: max,
          divisions: (max - min).round(),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildDropdownRow(ThemeData theme, String label, IconData icon,
      String value, List<String> items, ValueChanged<String?> onChanged) {
    return Row(
      children: [
        Icon(icon,
            size: 18,
            color: theme.colorScheme.onSurface.withValues(alpha: 0.6)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(label,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.7),
              )),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          decoration: BoxDecoration(
            border: Border.all(
                color: theme.colorScheme.outline.withValues(alpha: 0.3)),
            borderRadius: BorderRadius.circular(10),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: value,
              isDense: true,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: theme.colorScheme.onSurface,
              ),
              items: items
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: onChanged,
            ),
          ),
        ),
      ],
    );
  }
}
