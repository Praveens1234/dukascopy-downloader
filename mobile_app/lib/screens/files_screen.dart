import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../services/api_service.dart';

class FilesScreen extends StatefulWidget {
  const FilesScreen({super.key});

  @override
  State<FilesScreen> createState() => _FilesScreenState();
}

class _FilesScreenState extends State<FilesScreen> {
  final ApiService _api = ApiService();
  List<Map<String, dynamic>> _files = [];
  bool _isLoading = true;
  final Set<String> _downloadingFiles = {};

  @override
  void initState() {
    super.initState();
    _loadFiles();
  }

  Future<void> _loadFiles() async {
    try {
      final files = await _api.getFiles();
      if (mounted) {
        setState(() {
          _files = files;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _deleteFile(String filename) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete File?'),
        content: Text('Delete $filename permanently?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('No')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Yes')),
        ],
      ),
    );

    if (confirm == true) {
      await _api.deleteFile(filename);
      _loadFiles();
    }
  }

  Future<void> _shareFile(String filename) async {
    if (_downloadingFiles.contains(filename)) return;

    setState(() => _downloadingFiles.add(filename));

    try {
      final baseUrl = await _api.getBaseUrl();
      if (baseUrl == null) return;

      final url = '$baseUrl/api/files/$filename';
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final tempDir = await getTemporaryDirectory();
        final file = File('${tempDir.path}/$filename');
        await file.writeAsBytes(response.bodyBytes);

        await Share.shareXFiles([XFile(file.path)], text: 'Downloaded CSV: $filename');
      } else {
        throw Exception('Download failed');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error sharing file: $e')));
      }
    } finally {
      if (mounted) {
        setState(() => _downloadingFiles.remove(filename));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Files')),
      body: RefreshIndicator(
        onRefresh: _loadFiles,
        child: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _files.isEmpty
              ? const Center(child: Text("No files found"))
              : ListView.builder(
                  itemCount: _files.length,
                  itemBuilder: (context, index) {
                    final file = _files[index];
                    final name = file['name'];
                    final size = file['size_human'];
                    final isDownloading = _downloadingFiles.contains(name);

                    return ListTile(
                      leading: const Icon(Icons.insert_drive_file_outlined),
                      title: Text(name),
                      subtitle: Text(size),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (isDownloading)
                            const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
                          else
                            IconButton(
                              icon: const Icon(Icons.share),
                              onPressed: () => _shareFile(name),
                            ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: Colors.red),
                            onPressed: () => _deleteFile(name),
                          ),
                        ],
                      ),
                    );
                  },
                ),
      ),
    );
  }
}
