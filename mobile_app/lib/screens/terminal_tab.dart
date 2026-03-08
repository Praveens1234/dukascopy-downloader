import 'package:flutter/material.dart';

class TerminalTab extends StatefulWidget {
  final List<String> logs;
  final Map<String, dynamic>? activeJobProgress;
  final VoidCallback onClear;

  const TerminalTab({super.key, required this.logs, this.activeJobProgress, required this.onClear});

  @override
  State<TerminalTab> createState() => _TerminalTabState();
}

class _TerminalTabState extends State<TerminalTab> {
  final ScrollController _scrollController = ScrollController();

  @override
  void didUpdateWidget(TerminalTab oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.logs.length > oldWidget.logs.length) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Color _getLogColor(String log) {
    if (log.contains('✓')) return Colors.greenAccent;
    if (log.contains('✗') || log.contains('ERROR') || log.contains('FATAL')) return Colors.redAccent;
    if (log.contains('───') || log.contains('═══') || log.contains('Starting')) return Colors.blueAccent;
    return Colors.white70;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (widget.activeJobProgress != null)
          Container(
            padding: const EdgeInsets.all(16),
            color: const Color(0xFF1A2234),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Job: ${widget.activeJobProgress!['job_id']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.blueAccent)),
                    Text('${(widget.activeJobProgress!['progress'] as num).round()}%', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.blueAccent)),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: (widget.activeJobProgress!['progress'] as num).toDouble() / 100,
                  backgroundColor: Colors.white12,
                  color: Colors.blueAccent,
                  minHeight: 8,
                  borderRadius: BorderRadius.circular(4),
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Status: ${widget.activeJobProgress!['status']}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                    Text('Days: ${widget.activeJobProgress!['completed_days']} / ${widget.activeJobProgress!['total_days']}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ],
            ),
          ),

        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          color: Colors.black,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  CircleAvatar(radius: 5, backgroundColor: Colors.red),
                  SizedBox(width: 8),
                  CircleAvatar(radius: 5, backgroundColor: Colors.yellow),
                  SizedBox(width: 8),
                  CircleAvatar(radius: 5, backgroundColor: Colors.green),
                  SizedBox(width: 16),
                  Text('Terminal Logs', style: TextStyle(color: Colors.grey, fontSize: 12, fontFamily: 'monospace')),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.delete_sweep, color: Colors.grey, size: 20),
                onPressed: widget.onClear,
                tooltip: 'Clear Logs',
              ),
            ],
          ),
        ),

        Expanded(
          child: Container(
            color: const Color(0xFF0C0C0C),
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            child: widget.logs.isEmpty
                ? const Center(child: Text('Waiting for logs...', style: TextStyle(color: Colors.grey, fontFamily: 'monospace')))
                : ListView.builder(
                    controller: _scrollController,
                    itemCount: widget.logs.length,
                    itemBuilder: (context, index) {
                      final log = widget.logs[index];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4.0),
                        child: Text(
                          log,
                          style: TextStyle(
                            color: _getLogColor(log),
                            fontFamily: 'monospace',
                            fontSize: 12,
                          ),
                        ),
                      );
                    },
                  ),
          ),
        ),
      ],
    );
  }
}
