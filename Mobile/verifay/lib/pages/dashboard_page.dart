import 'package:flutter/material.dart';

class DashboardPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Dashboard'),
      automaticallyImplyLeading: false,
      
      ),
      body: Center(child: Text('Conteúdo do Dashboard')
      
      ),
    );
  }
}