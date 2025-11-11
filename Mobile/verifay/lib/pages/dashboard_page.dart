import 'package:flutter/material.dart';
import '../services/dashboard_service.dart';

class DashboardPage extends StatefulWidget {
  final Function(int)? onNavigate;

  const DashboardPage({this.onNavigate});

  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  List<dynamic> _detections = [];
  bool _loading = true;
  int _totalMessages = 0;
  int _spamCount = 0;
  int _safeCount = 0;
  String _spamPercent = '0%';

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    setState(() => _loading = true);

    try {
      final detections = await DashboardService.getLast10Detections();

      setState(() {
        _detections = detections;
        _totalMessages = detections.length;
        _spamCount = detections
            .where(
              (d) =>
                  d['result']['is_spam'] == 1 || d['result']['is_spam'] == true,
            )
            .length;
        _safeCount = detections
            .where(
              (d) =>
                  d['result']['is_spam'] == 0 ||
                  d['result']['is_spam'] == false,
            )
            .length;

        if (_totalMessages > 0) {
          double spamPercentage = (_spamCount / _totalMessages) * 100;
          _spamPercent = '${spamPercentage.toStringAsFixed(2)}%';
        } else {
          _spamPercent = '0%';
        }
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Erro ao carregar dados: $e')));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.black,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadDashboardData,
          ),
        ],
      ),
      body: _loading
          ? Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                physics: AlwaysScrollableScrollPhysics(),
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Estatísticas Gerais',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatCard(
                            'Total',
                            _totalMessages.toString(),
                            Icons.mail_outline,
                            Colors.blue,
                          ),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: _buildStatCard(
                            'Spam',
                            _spamCount.toString(),
                            Icons.warning_amber_rounded,
                            Colors.red,
                          ),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: _buildStatCard(
                            'Seguras',
                            _safeCount.toString(),
                            Icons.check_circle_outline,
                            Colors.green,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 24),
                    Card(
                      elevation: 2,
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          children: [
                            Text(
                              'Distribuição de Mensagens',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.grey[800],
                              ),
                            ),
                            SizedBox(height: 8),
                            Text(
                              'Média de Spam: $_spamPercent',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                            SizedBox(height: 20),
                            SizedBox(
                              height: 150,
                              child: Row(
                                mainAxisAlignment:
                                    MainAxisAlignment.spaceEvenly,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  _buildBarChart(
                                    'Spam',
                                    _spamCount,
                                    _totalMessages,
                                    Colors.red,
                                  ),
                                  _buildBarChart(
                                    'Seguras',
                                    _safeCount,
                                    _totalMessages,
                                    Colors.green,
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Últimas 10 Detecções',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[800],
                          ),
                        ),
                        TextButton.icon(
                          onPressed: () {
                            if (widget.onNavigate != null) {
                              widget.onNavigate!(2);
                            }
                          },
                          icon: Icon(Icons.history),
                          label: Text('Ver tudo'),
                        ),
                      ],
                    ),
                    SizedBox(height: 12),
                    _detections.isEmpty
                        ? Center(
                            child: Padding(
                              padding: EdgeInsets.all(32),
                              child: Column(
                                children: [
                                  Icon(
                                    Icons.inbox_outlined,
                                    size: 64,
                                    color: Colors.grey,
                                  ),
                                  SizedBox(height: 16),
                                  Text(
                                    'Nenhuma detecção encontrada',
                                    style: TextStyle(color: Colors.grey[600]),
                                  ),
                                ],
                              ),
                            ),
                          )
                        : Column(
                            children: _detections.map((detection) {
                              return _buildDetectionCard(detection);
                            }).toList(),
                          ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: color),
            SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBarChart(String label, int value, int total, Color color) {
    double percentage = total > 0 ? (value / total) : 0;
    double height = percentage * 120;
    if (height < 20 && value > 0) height = 20;

    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        Text(
          '${(percentage * 100).toStringAsFixed(0)}%',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        SizedBox(height: 8),
        Container(
          width: 60,
          height: height > 0 ? height : 10,
          decoration: BoxDecoration(
            color: color.withOpacity(0.7),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              value.toString(),
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        SizedBox(height: 8),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[700])),
      ],
    );
  }

  Widget _buildDetectionCard(Map<String, dynamic> detection) {
    bool isSpam =
        detection['result']['is_spam'] == 1 ||
        detection['result']['is_spam'] == true;
    String message = detection['result']['message'] ?? '';
    String date = _formatDate(detection['createdAt']);

    return Card(
      margin: EdgeInsets.only(bottom: 12),
      elevation: 1,
      child: ListTile(
        leading: Icon(
          isSpam ? Icons.warning_amber_rounded : Icons.check_circle_outline,
          color: isSpam ? Colors.red[600] : Colors.green[600],
          size: 32,
        ),
        title: Text(
          message.length > 50 ? '${message.substring(0, 50)}...' : message,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Text(
          date,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
        trailing: Chip(
          label: Text(
            isSpam ? 'SPAM' : 'SEGURO',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          backgroundColor: isSpam ? Colors.red[600] : Colors.green[600],
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
        ),
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      DateTime date = DateTime.parse(dateString);
      DateTime now = DateTime.now();
      Duration diff = now.difference(date);

      if (diff.inMinutes < 1) return 'Agora';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m atrás';
      if (diff.inHours < 24) return '${diff.inHours}h atrás';
      if (diff.inDays < 7) return '${diff.inDays}d atrás';

      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return 'Data inválida';
    }
  }
}
