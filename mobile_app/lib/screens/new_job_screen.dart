import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../models/download_request.dart';

class NewJobScreen extends StatefulWidget {
  const NewJobScreen({super.key});

  @override
  State<NewJobScreen> createState() => _NewJobScreenState();
}

class _NewJobScreenState extends State<NewJobScreen> {
  final ApiService _api = ApiService();
  final _formKey = GlobalKey<FormState>();

  // Config
  List<String> _availableSymbols = [];
  List<String> _availableTimeframes = [];
  bool _isLoadingConfig = true;

  // Form Data
  final Set<String> _selectedSymbols = {};
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 30));
  DateTime _endDate = DateTime.now();
  String _timeframe = 'M1';
  int _threads = 5;
  String _dataSource = 'auto';
  String _priceType = 'BID';
  String _volumeType = 'TOTAL';

  // Custom Timeframe
  final TextEditingController _customTfValue = TextEditingController(text: '120');
  String _customTfUnit = 'm';

  // Custom Symbol
  final TextEditingController _customSymbolController = TextEditingController();

  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _loadConfig();
  }

  @override
  void dispose() {
    _customTfValue.dispose();
    _customSymbolController.dispose();
    super.dispose();
  }

  Future<void> _loadConfig() async {
    try {
      final config = await _api.getConfig();
      if (mounted) {
        setState(() {
          _availableSymbols = List<String>.from(config['symbols']);
          _availableTimeframes = List<String>.from(config['timeframes']);
          if (!_availableTimeframes.contains('CUSTOM')) {
            _availableTimeframes.add('CUSTOM');
          }
          _isLoadingConfig = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to load config: $e')));
        setState(() => _isLoadingConfig = false);
      }
    }
  }

  void _addCustomSymbol() {
    final symbol = _customSymbolController.text.trim().toUpperCase();
    if (symbol.isNotEmpty && !_availableSymbols.contains(symbol)) {
      setState(() {
        _availableSymbols.insert(0, symbol); // Add to the beginning of the list
        _selectedSymbols.add(symbol); // Auto-select the newly added symbol
        _customSymbolController.clear();
      });
    } else if (symbol.isNotEmpty && _availableSymbols.contains(symbol)) {
      setState(() {
         _selectedSymbols.add(symbol);
         _customSymbolController.clear();
      });
    }
  }

  Future<void> _selectDate(BuildContext context, bool isStart) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: isStart ? _startDate : _endDate,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        if (isStart) _startDate = picked;
        else _endDate = picked;
      });
    }
  }

  void _submit() async {
    if (_selectedSymbols.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Select at least one symbol')));
      return;
    }

    setState(() => _isSubmitting = true);

    String? customTfStr;
    if (_timeframe == 'CUSTOM') {
      customTfStr = "${_customTfValue.text}$_customTfUnit";
    }

    final req = DownloadRequest(
      symbols: _selectedSymbols.toList(),
      startDate: DateFormat('yyyy-MM-dd').format(_startDate),
      endDate: DateFormat('yyyy-MM-dd').format(_endDate),
      timeframe: _timeframe,
      threads: _threads,
      dataSource: _dataSource,
      priceType: _priceType,
      volumeType: _volumeType,
      customTf: customTfStr,
    );

    try {
      await _api.startDownload(req);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Job started!')));
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("New Download")),
      body: _isLoadingConfig
          ? const Center(child: CircularProgressIndicator())
          : Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // Symbols Area
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Symbols (${_selectedSymbols.length} selected)',
                        style: Theme.of(context).textTheme.titleMedium),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Custom Symbol Input
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _customSymbolController,
                          decoration: const InputDecoration(
                            labelText: 'Add Custom Symbol',
                            hintText: 'e.g. BTCUSD',
                            border: OutlineInputBorder(),
                            isDense: true,
                          ),
                          onSubmitted: (_) => _addCustomSymbol(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        onPressed: _addCustomSymbol,
                        icon: const Icon(Icons.add_circle),
                        color: Theme.of(context).primaryColor,
                        iconSize: 32,
                        tooltip: 'Add Symbol',
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Symbol Chips
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _availableSymbols.map((s) {
                      final isSelected = _selectedSymbols.contains(s);
                      return FilterChip(
                        label: Text(s),
                        selected: isSelected,
                        onSelected: (bool selected) {
                          setState(() {
                            if (selected) _selectedSymbols.add(s);
                            else _selectedSymbols.remove(s);
                          });
                        },
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),

                  // Dates
                  Row(
                    children: [
                      Expanded(
                        child: InkWell(
                          onTap: () => _selectDate(context, true),
                          child: InputDecorator(
                            decoration: const InputDecoration(labelText: 'Start Date', border: OutlineInputBorder()),
                            child: Text(DateFormat('yyyy-MM-dd').format(_startDate)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: InkWell(
                          onTap: () => _selectDate(context, false),
                          child: InputDecorator(
                            decoration: const InputDecoration(labelText: 'End Date', border: OutlineInputBorder()),
                            child: Text(DateFormat('yyyy-MM-dd').format(_endDate)),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Timeframe
                  DropdownButtonFormField<String>(
                    value: _timeframe,
                    decoration: const InputDecoration(labelText: 'Timeframe', border: OutlineInputBorder()),
                    items: _availableTimeframes.map((tf) => DropdownMenuItem(value: tf, child: Text(tf))).toList(),
                    onChanged: (val) => setState(() => _timeframe = val!),
                  ),

                  if (_timeframe == 'CUSTOM') ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                         Expanded(
                           child: TextFormField(
                             controller: _customTfValue,
                             keyboardType: TextInputType.number,
                             decoration: const InputDecoration(labelText: 'Value', border: OutlineInputBorder()),
                           ),
                         ),
                         const SizedBox(width: 8),
                         Expanded(
                           child: DropdownButtonFormField<String>(
                             value: _customTfUnit,
                             decoration: const InputDecoration(labelText: 'Unit', border: OutlineInputBorder()),
                             items: const [
                               DropdownMenuItem(value: 's', child: Text('Seconds')),
                               DropdownMenuItem(value: 'm', child: Text('Minutes')),
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

                  // Advanced Options Expansion
                  ExpansionTile(
                    title: const Text('Advanced Options'),
                    children: [
                      DropdownButtonFormField<String>(
                        value: _dataSource,
                        decoration: const InputDecoration(labelText: 'Data Source'),
                        items: const [
                          DropdownMenuItem(value: 'auto', child: Text('Auto (Recommended)')),
                          DropdownMenuItem(value: 'tick', child: Text('Tick → Candle')),
                          DropdownMenuItem(value: 'native', child: Text('Native OHLC')),
                        ],
                        onChanged: (val) => setState(() => _dataSource = val!),
                      ),
                      DropdownButtonFormField<String>(
                        value: _priceType,
                        decoration: const InputDecoration(labelText: 'Price Type'),
                        items: const [
                          DropdownMenuItem(value: 'BID', child: Text('BID')),
                          DropdownMenuItem(value: 'ASK', child: Text('ASK')),
                          DropdownMenuItem(value: 'MID', child: Text('MID')),
                        ],
                        onChanged: (val) => setState(() => _priceType = val!),
                      ),
                       DropdownButtonFormField<String>(
                        value: _volumeType,
                        decoration: const InputDecoration(labelText: 'Volume Type'),
                        items: const [
                          DropdownMenuItem(value: 'TOTAL', child: Text('Total')),
                          DropdownMenuItem(value: 'BID', child: Text('Bid Volume')),
                          DropdownMenuItem(value: 'ASK', child: Text('Ask Volume')),
                          DropdownMenuItem(value: 'TICKS', child: Text('Tick Count')),
                        ],
                        onChanged: (val) => setState(() => _volumeType = val!),
                      ),
                      const SizedBox(height: 16),
                      Text('Threads: $_threads'),
                      Slider(
                        min: 1, max: 20, divisions: 19,
                        value: _threads.toDouble(),
                        onChanged: (v) => setState(() => _threads = v.toInt()),
                      ),
                    ],
                  ),

                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: _isSubmitting ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Theme.of(context).primaryColor,
                      foregroundColor: Colors.white,
                    ),
                    child: _isSubmitting
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Start Download'),
                  ),
                ],
              ),
            ),
    );
  }
}
