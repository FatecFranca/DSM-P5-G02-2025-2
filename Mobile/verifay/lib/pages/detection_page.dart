import 'package:flutter/material.dart';
import '../services/detection_service.dart';

class DetectionPage extends StatefulWidget {
  @override
  _DetectionPageState createState() => _DetectionPageState();
}

class _DetectionPageState extends State<DetectionPage> {
  final TextEditingController _messageController = TextEditingController();
  Map<String, dynamic>? _result;
  bool _loading = false;

  Future<void> _detectSpam() async {
    if (_messageController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Por favor, insira um texto para analisar')),
      );
      return;
    }

    setState(() {
      _loading = true;
    });

    try {
      final result = await DetectionService.detectText(_messageController.text);
      setState(() {
        _result = result;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Análise concluída com sucesso!'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao analisar: $e'),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 3),
        ),
      );
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Detecção de Spam', style: TextStyle(color: Colors.white)),
        backgroundColor: Colors.black,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              elevation: 2,
              color: Colors.grey[50],
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  children: [
                    Icon(Icons.info_outline, size: 30, color: Colors.blue[600]),
                    SizedBox(height: 8),
                    Text(
                      'Como funciona?',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Digite ou cole qualquer texto no campo abaixo. Nossa inteligência artificial irá analisar o conteúdo e identificar se é spam ou não.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            SizedBox(height: 24),

            // Campo de texto
            Text(
              'Texto para análise:',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.grey[800],
              ),
            ),
            SizedBox(height: 8),
            TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText:
                    'Ex: Parabéns! Você ganhou um prêmio de R\$ 10.000...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.black, width: 2),
                ),
                filled: true,
                fillColor: Colors.grey[50],
                contentPadding: EdgeInsets.all(16),
              ),
              maxLines: 4,
              minLines: 3,
            ),

            SizedBox(height: 24),

            // Botão centralizado
            Center(
              child: SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _loading ? null : _detectSpam,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(25),
                    ),
                    elevation: 2,
                  ),
                  child: _loading
                      ? Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                              ),
                            ),
                            SizedBox(width: 12),
                            Text(
                              'Analisando...',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        )
                      : Text(
                          'Detectar Spam',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                ),
              ),
            ),

            SizedBox(height: 24),

            // Resultado
            if (_result != null)
              Card(
                elevation: 3,
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _result!['result']['is_spam'] == true ||
                                    _result!['result']['is_spam'] == 1
                                ? Icons.warning_amber_rounded
                                : Icons.check_circle_outline,
                            color:
                                _result!['result']['is_spam'] == true ||
                                    _result!['result']['is_spam'] == 1
                                ? Colors.red[600]
                                : Colors.green[600],
                            size: 28,
                          ),
                          SizedBox(width: 12),
                          Text(
                            'Resultado da Análise',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey[800],
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 16),
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color:
                              _result!['result']['is_spam'] == true ||
                                  _result!['result']['is_spam'] == 1
                              ? Colors.red[50]
                              : Colors.green[50],
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color:
                                _result!['result']['is_spam'] == true ||
                                    _result!['result']['is_spam'] == 1
                                ? Colors.red[200]!
                                : Colors.green[200]!,
                          ),
                        ),
                        child: Text(
                          _result!['result']['is_spam'] == true ||
                                  _result!['result']['is_spam'] == 1
                              ? '🚨 SPAM DETECTADO'
                              : '✅ TEXTO SEGURO',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color:
                                _result!['result']['is_spam'] == true ||
                                    _result!['result']['is_spam'] == 1
                                ? Colors.red[700]
                                : Colors.green[700],
                          ),
                        ),
                      ),
                      SizedBox(height: 12),
                      Divider(),
                      SizedBox(height: 8),
                      _buildResultRow(
                        'ID da Análise:',
                        '${_result!['detectionId']}',
                      ),
                      SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: () {
                            _messageController.clear();
                            setState(() {
                              _result = null;
                            });
                          },
                          icon: Icon(Icons.refresh),
                          label: Text('Nova Análise'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.black,
                            foregroundColor: Colors.white,
                            padding: EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
          ),
          Expanded(
            child: Text(value, style: TextStyle(color: Colors.grey[800])),
          ),
        ],
      ),
    );
  }
}
