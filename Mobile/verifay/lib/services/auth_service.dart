import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String _baseUrl = 'http://20.206.201.3:3000';
  static String? _token;

  static String? get token => _token;

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['token'] != null) {
        _token = data['token'];
        await _saveToken(data['token']);
        return {'success': true, 'token': data['token']};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Erro no login',
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Erro de conexão: $e'};
    }
  }

  static Future<Map<String, dynamic>> register(
    String email,
    String name,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'name': name, 'password': password}),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {'success': true, 'message': 'Usuário criado com sucesso'};
      } else {
        return {
          'success': false,
          'message': data['message'] ?? 'Erro no registro',
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Erro de conexão: $e'};
    }
  }

  static Future<void> _saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }

  static Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }

  static Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }

  static bool isLoggedIn() {
    return _token != null && _token!.isNotEmpty;
  }

  static Map<String, String> get authHeaders => {
    'Content-Type': 'application/json',
    if (_token != null) 'Authorization': 'Bearer $_token',
  };
}
