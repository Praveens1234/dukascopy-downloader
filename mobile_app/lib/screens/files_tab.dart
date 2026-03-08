import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class FilesTab extends StatelessWidget {
  final String serverUrl;
  final List<dynamic> files;
  final VoidCallback onRefresh;

  const FilesTab({
    super.key,
    required this.serverUrl,
    required this.files,
    required this.onRefresh,
  });

  Future<void> _shareFile(BuildContext context, String filename) async {
    try {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => const Center(child: CircularProgressIndicator()),
      );

      final response = await http.get(Uri.parse('$serverUrl/api/files/$filename'));
      if (response.statusCode == 200) {
        final dir = await getTemporaryDirectory();
        final file = File('${dir.path}/$filename');
        await file.writeAsBytes(response.bodyBytes);

        if (context.mounted) Navigator.pop(context); // Close loading

        await Share.shareXFiles([XFile(file.path)], text: 'Downloaded from Dukascopy Downloader');
      } else {
        if (context.mounted) Navigator.pop(context); // Close loading
        if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to fetch file for sharing')));
      }
    } catch (e) {
      if (context.mounted) Navigator.pop(context); // Close loading
      if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> _deleteFile(BuildContext context, String filename) async {
    final bool? confirm = await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete File'),
        content: Text('Are you sure you want to delete $filename?'),
        actions: [
          TextButton(onPressed: () => Navigator.of(ctx).pop(false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.of(ctx).pop(true), child: const Text('Delete', style: TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirm == true) {
      try {
        final res = await http.delete(Uri.parse('$serverUrl/api/files/$filename'));
        if (res.statusCode == 200) {
          if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('File deleted')));
          onRefresh();
        } else {
          if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to delete file')));
        }
      } catch (e) {
        if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (files.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.folder_open, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No downloaded files', style: TextStyle(color: Colors.grey)),
            TextButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh'),
            )
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(8),
        itemCount: files.length,
        itemBuilder: (context, index) {
          final file = files[index];
          return Card(
            child: ListTile(
              leading: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.description, color: Colors.blue),
              ),
              title: Text(file['name'], style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14)),
              subtitle: Text('${file['size_human']} • ${DateTime.parse(file['modified']).toLocal().toString().split('.')[0]}', style: const TextStyle(color: Colors.grey, fontSize: 12)),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.share, color: Colors.blue),
                    tooltip: 'Share File',
                    onPressed: () => _shareFile(context, file['name']),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, color: Colors.redAccent),
                    tooltip: 'Delete File',
                    onPressed: () => _deleteFile(context, file['name']),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
