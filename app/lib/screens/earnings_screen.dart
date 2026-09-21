import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../api_config.dart';

class EarningsScreen extends StatefulWidget {
  const EarningsScreen({super.key});

  @override
 State<EarningsScreen> createState() => _EarningsScreenState();
}
class _EarningsScreenState extends State<EarningsScreen> {
 
 Map<String, dynamic>? dashboardData;
  bool isLoading = true;
Future<void> fetchDashboard() async {
  try {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/dashboard/recycler/1'),
    );

    if (response.statusCode == 200) {
      setState(() {
        dashboardData = jsonDecode(response.body);
        isLoading = false;
      });
    } else {
      setState(() {
        isLoading = false;
      });
    }
  } catch (e) {
    setState(() {
      isLoading = false;
    });
  }
}


@override
  void initState() {
    super.initState();
    fetchDashboard();
  }


 @override


  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Earnings Dashboard'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: isLoading
    ? const Center(
        child: CircularProgressIndicator(),
      )
    : SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
 if (dashboardData != null)
      Text(
        'Total Lots Received: ${dashboardData!['total_lots_received'] ?? 0}',
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),



            Card(
              color: Colors.orange.shade50,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children:  [
                    Text(
                      'Total Earnings',
                      style: TextStyle(fontSize: 18),
                    ),
                    SizedBox(height: 8),
                    Text(
                      '₹${dashboardData?['lots']?.fold(0.0, (sum, lot) => sum + (lot['price_min'] ?? 0)) ?? 0}',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: _earningCard(
                    'Today',
                    '₹850',
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _earningCard(
                    'This Week',
                    '₹3,450',
                    Colors.blue,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 25),

            const Text(
              'Recent Transactions',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 12),

            _transaction(
              'Plastic Pickup',
              'Today',
              '₹450',
            ),
            _transaction(
              'Paper Pickup',
              'Yesterday',
              '₹300',
            ),
            _transaction(
              'Metal Pickup',
              '18 Sep',
              '₹650',
            ),
            _transaction(
              'Cardboard Pickup',
              '17 Sep',
              '₹250',
            ),
          ],
        ),
      ),
    );
  }

  static Widget _earningCard(
    String title,
    String amount,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(title),
            const SizedBox(height: 8),
            Text(
              amount,
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  static Widget _transaction(
    String title,
    String date,
    String amount,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: const CircleAvatar(
          child: Icon(Icons.currency_rupee),
        ),
        title: Text(title),
        subtitle: Text(date),
        trailing: Text(
          amount,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.green,
          ),
        ),
      ),
    );
  }
}