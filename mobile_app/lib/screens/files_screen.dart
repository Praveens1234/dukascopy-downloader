import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../providers/server_provider.dart';
import '../models/download_file.dart';

class FilesScreen extends StatefulWidget {
  const FilesScreen({super.key});

  @override
  State<FilesScreen> createState() => _FilesScreenState();
}

class _FilesScreenState extends State<FilesScreen>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServerProvider>().loadFiles();
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final theme = Theme.of(context);
    final provider = context.watch<ServerProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Files'),
        actions: [
          if (provider.files.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: Chip(
                label: Text('${provider.files.length} files',
                    style: TextStyle(
                        fontSize: 12, color: theme.colorScheme.primary)),
                backgroundColor:
                    theme.colorScheme.primary.withValues(alpha: 0.1),
                side: BorderSide(
                    color: theme.colorScheme.primary.withValues(alpha: 0.2)),
                visualDensity: VisualDensity.compact,
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: provider.loadFiles,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: provider.loadFiles,
        child: provider.isLoadingFiles && provider.files.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : provider.files.isEmpty
                ? _buildEmptyState(theme)
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.files.length,
                    itemBuilder: (context, index) {
                      return _FileCard(file: provider.files[index]);
                    },
                  ),
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.folder_off_rounded,
              size: 64,
              color: theme.colorScheme.onSurface.withValues(alpha: 0.2)),
          const SizedBox(height: 16),
          Text('No files yet',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: theme.colorScheme.onSurface.withValues(alpha: 0.4),
              )),
          const SizedBox(height: 8),
          Text('Downloaded CSV files will appear here',
              style: TextStyle(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.3),
              )),
        ],
      ),
    );
  }
}

class _FileCard extends StatelessWidget {
  final DownloadFile file;

  const _FileCard({required this.file});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final provider = context.read<ServerProvider>();

    // Parse symbol and date from filename
    final parts = file.name.replaceAll('.csv', '').split('-');
    final symbol = parts.isNotEmpty ? parts[0] : file.name;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Card(
        child: InkWell(
          onTap: () => _showFileOptions(context, provider),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                // File icon
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(Icons.description_rounded,
                      color: theme.colorScheme.primary, size: 22),
                ),
                const SizedBox(width: 14),
                // File info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        symbol,
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        file.name,
                        style: TextStyle(
                          fontSize: 12,
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.5),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                // Size and actions
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color:
                            theme.colorScheme.primary.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        file.sizeHuman,
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 11,
                          fontWeight: FontWeight.w500,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Icon(Icons.chevron_right_rounded,
                        size: 20,
                        color: theme.colorScheme.onSurface
                            .withValues(alpha: 0.3)),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showFileOptions(BuildContext context, ServerProvider provider) {
    final theme = Theme.of(context);

    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color:
                        theme.colorScheme.onSurface.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 20),
                Text(file.name,
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    )),
                Text(file.sizeHuman,
                    style: TextStyle(
                      color:
                          theme.colorScheme.onSurface.withValues(alpha: 0.5),
                    )),
                const SizedBox(height: 20),
                _buildOptionTile(
                  context,
                  icon: Icons.open_in_browser_rounded,
                  label: 'Open in Browser',
                  subtitle: 'Download via browser',
                  onTap: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                            'Open this URL in browser:\n${provider.api.getFileDownloadUrl(file.name)}'),
                        duration: const Duration(seconds: 5),
                      ),
                    );
                  },
                ),
                _buildOptionTile(
                  context,
                  icon: Icons.delete_outline_rounded,
                  label: 'Delete File',
                  subtitle: 'Remove from server',
                  isDestructive: true,
                  onTap: () {
                    Navigator.pop(context);
                    _confirmDelete(context, provider);
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildOptionTile(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String subtitle,
    required VoidCallback onTap,
    bool isDestructive = false,
  }) {
    final theme = Theme.of(context);
    final color = isDestructive
        ? theme.colorScheme.error
        : theme.colorScheme.onSurface;

    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(label, style: TextStyle(color: color)),
      subtitle: Text(subtitle),
      onTap: onTap,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    );
  }

  void _confirmDelete(BuildContext context, ServerProvider provider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete File'),
        content: Text('Are you sure you want to delete ${file.name}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.pop(context);
              final success = await provider.deleteFile(file.name);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                        success ? 'File deleted' : 'Failed to delete file'),
                  ),
                );
              }
            },
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
