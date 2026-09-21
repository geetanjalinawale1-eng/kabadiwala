import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import 'dart:convert';
import 'package:http/http.dart' as http;

class HandoverScreen extends StatefulWidget {
  const HandoverScreen({super.key});

  @override
  State<HandoverScreen> createState() => _HandoverScreenState();
}

class _HandoverScreenState extends State<HandoverScreen> {
  String? scannedCode;

  Map<String, dynamic>? lotDetails;
  bool isLoadingLot = false;

 void openScanner() {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => QRScannerScreen(
        onScan: (code) async {
          setState(() {
            scannedCode = code;
            isLoadingLot = true;
          });

          try {
            final uri = Uri.parse('http://$code');

            final response = await http.get(uri);

            if (response.statusCode == 200) {
              setState(() {
                lotDetails = jsonDecode(response.body);
                isLoadingLot = false;
              });
            } else {
              setState(() {
                isLoadingLot = false;
              });
            }
          } catch (e) {
            setState(() {
              isLoadingLot = false;
            });
          }
        },
      ),
    ),
  );
}
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('QR Scan & Handover'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Text(
              'Scan Customer QR Code',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 25),

            GestureDetector(
              onTap: openScanner,
              child: Container(
                height: 220,
                width: 220,
                decoration: BoxDecoration(
                  border: Border.all(
                    color: Colors.blue,
                    width: 3,
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Icon(
                    Icons.qr_code_scanner,
                    size: 150,
                    color: Colors.blue,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 15),

            ElevatedButton.icon(
              onPressed: openScanner,
              icon: const Icon(Icons.camera_alt),
              label: const Text('Open QR Scanner'),
            ),

            if (scannedCode != null) ...[
  const SizedBox(height: 20),

  if (isLoadingLot)
    const CircularProgressIndicator(),

  if (!isLoadingLot && lotDetails != null)
    Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Lot Details',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 15),

            ListTile(
              leading: const Icon(Icons.recycling),
              title: const Text('Material'),
              trailing: Text(
                lotDetails!['material_type']?.toString() ?? '-',
              ),
            ),

            ListTile(
              leading: const Icon(Icons.scale),
              title: const Text('Weight'),
              trailing: Text(
                '${lotDetails!['weight_kg']?.toString() ?? '-'} kg',
              ),
            ),

            ListTile(
              leading: const Icon(Icons.currency_rupee),
              title: const Text('Price'),
              trailing: Text(
                '₹${lotDetails!['price_min']?.toString() ?? '-'}',
              ),
            ),

            ListTile(
              leading: const Icon(Icons.info),
              title: const Text('Status'),
              trailing: Text(
                lotDetails!['status']?.toString() ?? '-',
              ),
            ),
          ],
        ),
      ),
    ),
],

            const SizedBox(height: 30),

            const Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'Handover Details',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            const SizedBox(height: 15),

            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: const [
                    ListTile(
                      leading: Icon(Icons.recycling),
                      title: Text('Material'),
                      trailing: Text('Plastic'),
                    ),
                    ListTile(
                      leading: Icon(Icons.scale),
                      title: Text('Weight'),
                      trailing: Text('8 kg'),
                    ),
                    ListTile(
                      leading: Icon(Icons.currency_rupee),
                      title: Text('Amount'),
                      trailing: Text('₹320'),
                    ),
                    ListTile(
                      leading: Icon(Icons.location_on),
                      title: Text('Pickup'),
                      trailing: Text('Kothrud, Pune'),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 25),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
onPressed: () async {
  try {
    final response = await http.post(
      Uri.parse(
  'http://10.2.9.126:8000/lots/1/handover?recycler_id=1&final_price=320',
),
    );

    if (response.statusCode == 200) {
if (!context.mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Handover completed successfully!'),
        ),
      );
    } else {
       
       if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Handover failed: ${response.body}'),
        ),
      );
    }
  } catch (e) {
       if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Error: $e'),
      ),
    );
  }
},
                
                icon: const Icon(Icons.check_circle),
                label: const Text('Confirm Handover'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    vertical: 16,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class QRScannerScreen extends StatefulWidget {
  final Function(String) onScan;

  const QRScannerScreen({
    super.key,
    required this.onScan,
  });

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  final MobileScannerController controller = MobileScannerController();
  bool scanned = false;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Customer QR'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: MobileScanner(
        controller: controller,
        onDetect: (capture) {
          if (scanned) return;

          final List<Barcode> barcodes = capture.barcodes;

          for (final barcode in barcodes) {
            final String? code = barcode.rawValue;

            if (code != null && code.isNotEmpty) {
              scanned = true;
              widget.onScan(code);
              Navigator.pop(context);
              break;
            }
          }
        },
      ),
    );
  }
}