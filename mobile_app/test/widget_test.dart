import 'package:flutter_test/flutter_test.dart';

import 'package:dukascopy_downloader/main.dart';

void main() {
  testWidgets('App renders connection screen', (WidgetTester tester) async {
    await tester.pumpWidget(const DukascopyApp());
    await tester.pumpAndSettle();

    // Verify that the connection screen is shown
    expect(find.text('Connect to Server'), findsOneWidget);
  });
}
