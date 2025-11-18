import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

class DashboardService {
  static const String _baseUrl = 'http://20.206.201.3:3000';

  static Future<List<dynamic>> getLast10Detections() async {
    try {
      print('📤 Buscando últimas 10 detecções...');

      final response = await http.get(
        Uri.parse('$_baseUrl/dashboard/last10'),
        headers: AuthService.authHeaders,
      );

      print('📥 Status Code: ${response.statusCode}');
      print('📥 Response Body (RAW): ${response.body}');

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body) as List<dynamic>;
        print('📥 Total de detecções: ${decoded.length}');
        return decoded;
      } else {
        throw Exception('Erro ao buscar detecções: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Exception: $e');
      throw Exception('Erro de conexão: $e');
    }
  }

  static Future<Map<String, dynamic>> getHistory() async {
    try {
      print('📤 Buscando histórico completo...');

      final response = await http.get(
        Uri.parse('$_baseUrl/dashboard/history'),
        headers: AuthService.authHeaders,
      );

      print('📥 Status Code: ${response.statusCode}');
      print('📥 Response Body (RAW): ${response.body}');

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        print('📥 Total: ${decoded['total']}');
        print('📥 Spam %: ${decoded['medias']?['spamPercent']}');
        return decoded;
      } else {
        throw Exception('Erro ao buscar histórico: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Exception: $e');
      throw Exception('Erro de conexão: $e');
    }
  }

  static Future<Map<String, dynamic>> getDetectionDetails(String id) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/dashboard/details/$id'),
        headers: AuthService.authHeaders,
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Erro ao buscar detalhes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erro de conexão: $e');
    }
  }
}
