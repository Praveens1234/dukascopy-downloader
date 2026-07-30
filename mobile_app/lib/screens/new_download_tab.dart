import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NewDownloadTab extends StatefulWidget {
  final String serverUrl;
  final Map<String, dynamic> config;
  final Function(String) onJobStarted;

  const NewDownloadTab({super.key, required this.serverUrl, required this.config, required this.onJobStarted});

  @override
  State<NewDownloadTab> createState() => _NewDownloadTabState();
}

class _NewDownloadTabState extends State<NewDownloadTab> {
  final Set<String> _selectedSymbols = {};
  final TextEditingController _customSymbolController = TextEditingController();
  final Set<String> _customSymbols = {};

  String _startDate = '2024-01-01';
  String _endDate = '2024-12-31';
  String _timeframe = 'M1';
  String _dataSource = 'auto';
  String _priceType = 'BID';
  String _volumeType = 'TOTAL';
  double _threads = 5.0;
  bool _isLoading = false;

  // Custom Timeframe
  String _customTfValue = '120';
  String _customTfUnit = 'm';

  @override
  void initState() {
    super.initState();
    final now = DateTime.now();
    _endDate = "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}";
  }

  void _addCustomSymbol() {
    final sym = _customSymbolController.text.trim().toUpperCase();
    if (sym.isNotEmpty && sym.length >= 3) {
      setState(() {
        _customSymbols.add(sym);
        _selectedSymbols.add(sym);
        _customSymbolController.clear();
      });
    }
  }

  Future<void> _selectDate(BuildContext context, bool isStart) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: isStart ? DateTime.parse(_startDate) : DateTime.parse(_endDate),
      firstDate: DateTime(2000),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        final formatted = "${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}";
        if (isStart) _startDate = formatted;
        else _endDate = formatted;
      });
    }
  }

  Future<void> _startDownload() async {
    if (_selectedSymbols.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Select at least one symbol')));
      return;
    }

    setState(() => _isLoading = true);

    String? customTf;
    if (_timeframe == 'CUSTOM') {
      customTf = '$_customTfValue$_customTfUnit';
    }

    try {
      final res = await http.post(
        Uri.parse('${widget.serverUrl}/api/download'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'symbols': _selectedSymbols.toList(),
          'start_date': _startDate,
          'end_date': _endDate,
          'timeframe': _timeframe,
          'threads': _threads.toInt(),
          'data_source': _dataSource,
          'price_type': _priceType,
          'volume_type': _volumeType,
          'custom_tf': customTf,
        }),
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (mounted) {
            widget.onJobStarted(data['job_id']);
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Download started')));
        }
      } else {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${res.statusCode}')));
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to start download: $e')));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final symbols = widget.config['symbols'] ?? [];
    final timeframes = widget.config['timeframes'] ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Symbols Section
          const Text('Symbols', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Container(
            height: 120,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.white24),
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.all(8),
            child: SingleChildScrollView(
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  ...symbols.map((sym) {
                    final isSelected = _selectedSymbols.contains(sym);
                    return ChoiceChip(
                      label: Text(sym),
                      selected: isSelected,
                      onSelected: (val) {
                        setState(() {
                          if (val) _selectedSymbols.add(sym);
                          else _selectedSymbols.remove(sym);
                        });
                      },
                    );
                  }),
                  ..._customSymbols.map((sym) {
                    final isSelected = _selectedSymbols.contains(sym);
                    return ChoiceChip(
                      label: Text(sym),
                      selected: isSelected,
                      selectedColor: Colors.deepPurple,
                      onSelected: (val) {
                        setState(() {
                          if (val) _selectedSymbols.add(sym);
                          else _selectedSymbols.remove(sym);
                        });
                      },
                    );
                  }),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _customSymbolController,
                  decoration: const InputDecoration(
                    hintText: 'Custom symbol (e.g. BTCUSD)',
                    isDense: true,
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _addCustomSymbol,
                child: const Text('Add'),
              ),
            ],
          ),

          const SizedBox(height: 24),
          const Text('Date Range', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.calendar_today, size: 16),
                  label: Text(_startDate),
                  onPressed: () => _selectDate(context, true),
                ),
              ),
              const Padding(padding: EdgeInsets.symmetric(horizontal: 8.0), child: Text('to')),
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.calendar_today, size: 16),
                  label: Text(_endDate),
                  onPressed: () => _selectDate(context, false),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),
          const Text('Configuration', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),

          DropdownButtonFormField<String>(
            decoration: const InputDecoration(labelText: 'Timeframe', border: OutlineInputBorder()),
            value: timeframes.contains(_timeframe) ? _timeframe : (timeframes.isNotEmpty ? timeframes.first : 'M1'),
            items: timeframes.map<DropdownMenuItem<String>>((tf) {
              return DropdownMenuItem<String>(value: tf, child: Text(tf));
            }).toList(),
            onChanged: (val) => setState(() => _timeframe = val!),
          ),

          if (_timeframe == 'CUSTOM') ...[
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    initialValue: _customTfValue,
                    decoration: const InputDecoration(labelText: 'Custom Value', border: OutlineInputBorder()),
                    keyboardType: TextInputType.number,
                    onChanged: (val) => _customTfValue = val,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    decoration: const InputDecoration(border: OutlineInputBorder()),
                    value: _customTfUnit,
                    items: const [
                      DropdownMenuItem(value: 's', child: Text('Secs')),
                      DropdownMenuItem(value: 'm', child: Text('Mins')),
                      DropdownMenuItem(value: 'h', child: Text('Hours')),
                      DropdownMenuItem(value: 'd', child: Text('Days')),
                    ],
                    onChanged: (val) => setState(() => _customTfUnit = val!),
                  ),
                ),
              ],
            ),
          ],

          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            decoration: const InputDecoration(labelText: 'Data Source', border: OutlineInputBorder()),
            value: _dataSource,
            items: const [
              DropdownMenuItem(value: 'auto', child: Text('Auto (Recommended)')),
              DropdownMenuItem(value: 'tick', child: Text('Tick → Candle')),
              DropdownMenuItem(value: 'native', child: Text('Native OHLC')),
            ],
            onChanged: (val) => setState(() => _dataSource = val!),
          ),

          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Price Type', border: OutlineInputBorder()),
                  value: _priceType,
                  items: const [
                    DropdownMenuItem(value: 'BID', child: Text('BID')),
                    DropdownMenuItem(value: 'ASK', child: Text('ASK')),
                    DropdownMenuItem(value: 'MID', child: Text('MID')),
                  ],
                  onChanged: (val) => setState(() => _priceType = val!),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: DropdownButtonFormField<String>(
                  decoration: const InputDecoration(labelText: 'Volume Type', border: OutlineInputBorder()),
                  value: _volumeType,
                  items: const [
                    DropdownMenuItem(value: 'TOTAL', child: Text('Total')),
                    DropdownMenuItem(value: 'BID', child: Text('Bid')),
                    DropdownMenuItem(value: 'ASK', child: Text('Ask')),
                    DropdownMenuItem(value: 'TICKS', child: Text('Ticks')),
                  ],
                  onChanged: (val) => setState(() => _volumeType = val!),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),
          Text('Threads: ${_threads.toInt()}'),
          Slider(
            value: _threads,
            min: 1,
            max: 20,
            divisions: 19,
            label: _threads.toInt().toString(),
            onChanged: (val) => setState(() => _threads = val),
          ),

          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _isLoading ? null : _startDownload,
            icon: _isLoading ? const CircularProgressIndicator() : const Icon(Icons.download),
            label: Text(_isLoading ? 'Starting...' : 'Start Download'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              backgroundColor: const Color(0xFF3B82F6),
              foregroundColor: Colors.white,
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }
}
