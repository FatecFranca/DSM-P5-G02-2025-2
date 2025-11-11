import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

class DetectionService {
  static const String _baseUrl = 'http://10.90.41.52:3000';

  static Future<Map<String, dynamic>> detectText(String message) async {
    try {
      print('📤 Enviando requisição para: $_baseUrl/detection/detect');
      print('📤 Mensagem: $message');

      final response = await http.post(
        Uri.parse('$_baseUrl/detection/detect'),
        headers: AuthService.authHeaders,
        body: jsonEncode({'message': message}),
      );

      print('📥 Status Code: ${response.statusCode}');
      print('📥 Response Body (RAW): ${response.body}');

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        print('📥 Response Decoded: $decoded');
        return decoded;
      } else {
        print('❌ Erro: Status ${response.statusCode}');
        throw Exception('Erro na detecção: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Exception: $e');
      throw Exception('Erro de conexão: $e');
    }
  }
}
