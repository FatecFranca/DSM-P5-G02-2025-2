import 'package:flutter/material.dart';
import '../pages/dashboard_page.dart';
import '../pages/detection_page.dart';
import '../pages/history_page.dart';

class NavigationMenu extends StatefulWidget {
  const NavigationMenu({super.key});

  @override
  _NavigationMenuState createState() => _NavigationMenuState();
}

class _NavigationMenuState extends State<NavigationMenu> {
  int _selectedIndex = 0;

  List<Widget> get _pages => [
    DashboardPage(
      onNavigate: (index) {
        setState(() {
          _selectedIndex = index;
        });
      },
    ),
    DetectionPage(),
    HistoryPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      bottomNavigationBar: NavigationBar(
        backgroundColor: Colors.black,
        animationDuration: Duration(seconds: 1),
        indicatorColor: const Color.fromARGB(167, 252, 251, 251),
        labelTextStyle: MaterialStateProperty.all(
          const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
        ),
        height: 80,
        elevation: 0,
        selectedIndex: _selectedIndex,
        onDestinationSelected: _onItemTapped,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home),
            label: "Início",
            selectedIcon: Icon(Icons.home_outlined),
          ),
          NavigationDestination(
            icon: Icon(Icons.chat_rounded),
            label: "Detecção",
          ),
          NavigationDestination(
            icon: Icon(Icons.punch_clock_outlined),
            label: "Historico",
          ),
        ],
      ),
      body: _pages[_selectedIndex],
    );
  }
}
