import 'package:flutter/material.dart';
import 'matching_list.dart';
import 'handover_screen.dart';
import 'earnings_screen.dart';

class RecyclerDashboard extends StatelessWidget {
  const RecyclerDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Recycler Dashboard'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Welcome, Recycler!',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 20),

            Row(
              children: [
                Expanded(
                  child: _statCard(
                    'Pending',
                    '5',
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _statCard(
                    'Completed',
                    '12',
                    Colors.green,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _statCard(
                    'Today Earnings',
                    '₹850',
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _statCard(
                    'Total Earnings',
                    '₹12,450',
                    Colors.purple,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 25),

            const Text(
              'Quick Actions',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 12),

            _actionButton(
              context,
              'Find Scrap Requests',
              Icons.search,
              Colors.green,
              const MatchingListScreen(),
            ),

            _actionButton(
              context,
              'Scan QR & Handover',
              Icons.qr_code_scanner,
              Colors.blue,
              const HandoverScreen(),
            ),

            _actionButton(
              context,
              'View Earnings',
              Icons.account_balance_wallet,
              Colors.orange,
              const EarningsScreen(),
            ),

            const SizedBox(height: 25),

            const Text(
              'Recent Pickups',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 12),

            _pickupCard(
              'Plastic',
              'Pune',
              '₹450',
              'Completed',
            ),

            _pickupCard(
              'Paper',
              'Wakad',
              '₹300',
              'Completed',
            ),

            _pickupCard(
              'Metal',
              'Baner',
              '₹650',
              'Pending',
            ),
          ],
        ),
      ),
    );
  }

  static Widget _statCard(
    String title,
    String value,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
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

  static Widget _actionButton(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    Widget screen,
  ) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      child: ElevatedButton.icon(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => screen,
            ),
          );
        },
        icon: Icon(icon),
        label: Text(title),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(
            vertical: 15,
          ),
        ),
      ),
    );
  }

  static Widget _pickupCard(
    String material,
    String location,
    String amount,
    String status,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: const CircleAvatar(
          child: Icon(Icons.recycling),
        ),
        title: Text(material),
        subtitle: Text(location),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              amount,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(status),
          ],
        ),
      ),
    );
  }
}