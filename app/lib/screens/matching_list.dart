import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../api_config.dart';

class MatchingListScreen extends StatefulWidget {
  const MatchingListScreen({super.key});

  @override
  State<MatchingListScreen> createState() => _MatchingListScreenState();
}

class _MatchingListScreenState extends State<MatchingListScreen> {
  List<dynamic> recyclers = [];
  bool isLoading = true;
  String selectedMaterial = 'Plastic';

  @override
  void initState() {
    super.initState();
    fetchRecyclers();
  }

  Future<void> fetchRecyclers() async {
    try {
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/recyclers/match?material_type=$selectedMaterial',
      );

      final response = await http.get(url);

      if (response.statusCode == 200) {
        setState(() {
          recyclers = jsonDecode(response.body);
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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Matching Recyclers'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : recyclers.isEmpty
              ? const Center(
                  child: Text('No matching recyclers found'),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: recyclers.length,
                  itemBuilder: (context, index) {
                    final recycler = recyclers[index];

                    return Card(
                      margin: const EdgeInsets.only(bottom: 14),
                      child: ListTile(
                        leading: const CircleAvatar(
                          child: Icon(Icons.recycling),
                        ),
                        title: Text(
                          recycler['name'] ?? 'Recycler',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        subtitle: Text(
                          'Accepted: ${recycler['accepted_materials'] ?? ''}',
                        ),
                        trailing: ElevatedButton(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Recycler selected!'),
                              ),
                            );
                          },
                          child: const Text('Select'),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}