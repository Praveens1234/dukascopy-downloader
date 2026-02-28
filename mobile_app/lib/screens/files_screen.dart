import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_saver/file_saver.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class FilesScreen extends StatefulWidget {
  const FilesScreen({super.key});

  @override
  State<FilesScreen> createState() => _FilesScreenState();
}

class _FilesScreenState extends State<FilesScreen> {
  final ApiService _api = ApiService();
  List<String> _files = [];
  bool _isLoading = true;
  final Set<String> _downloadingFiles = {};

  @override
  void initState() {
    super.initState();
    _loadFiles();
  }

  Future<void> _loadFiles() async {
    try {
      final files = await _api.listFiles();
      if (mounted) {
        setState(() {
          _files = files;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to load files: $e')));
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _downloadFile(String filename) async {
    setState(() => _downloadingFiles.add(filename));
    try {
      final prefs = await SharedPreferences.getInstance();
      final url = prefs.getString('server_url');

      final response = await http.get(Uri.parse('$url/api/files/$filename'));
      if (response.statusCode == 200) {
        Uint8List bytes = response.bodyBytes;

        String ext = filename.contains('.') ? filename.split('.').last : 'csv';
        String nameWithoutExt = filename.contains('.') ? filename.substring(0, filename.lastIndexOf('.')) : filename;

        await FileSaver.instance.saveFile(
          name: nameWithoutExt,
          bytes: bytes,
          ext: ext,
          mimeType: MimeType.csv,
        );

        if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Saved $filename successfully')));
        }
      } else {
        throw Exception('Failed to download: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Download error: $e')));
      }
    } finally {
      if (mounted) {
        setState(() => _downloadingFiles.remove(filename));
      }
    }
  }

  Future<void> _deleteFile(String filename) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Confirm Delete'),
        content: Text('Are you sure you want to delete $filename from the server?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Cancel')),
          TextButton(onPressed: () => Navigator.pop(c, true), child: const Text('Delete', style: TextStyle(color: Colors.red))),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _api.deleteFile(filename);
        _loadFiles();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Delete error: $e')));
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Generated Files'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadFiles),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _files.isEmpty
              ? const Center(child: Text('No files found on server.'))
              : ListView.builder(
                  itemCount: _files.length,
                  itemBuilder: (context, index) {
                    final filename = _files[index];
                    final isDownloading = _downloadingFiles.contains(filename);
                    return ListTile(
                      leading: const Icon(Icons.insert_drive_file),
                      title: Text(filename),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          isDownloading
                            ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
                            : IconButton(
                                icon: const Icon(Icons.download),
                                tooltip: 'Download and Save',
                                onPressed: () => _downloadFile(filename),
                              ),
                          IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => _deleteFile(filename),
                          ),
                        ],
                      ),
                    );
                  },
                ),
    );
  }
}
