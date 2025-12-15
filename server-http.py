#!/usr/bin/env python3
"""
シンプルなHTTPサーバー
localhostで実行すれば、ブラウザのセキュリティ制限により位置情報APIが動作します
"""

import http.server
import socketserver
import os
from pathlib import Path

# カレントディレクトリを取得
os.chdir(Path(__file__).parent)

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS対応
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # キャッシュ無効
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # ログの見やすさを改善
        print(f"[{self.client_address[0]}] {format%args}")

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🚀 HTTPサーバーが起動しました")
    print(f"📍 ブラウザで以下にアクセスしてください:")
    print(f"   http://localhost:{PORT}/bike-parking-finder.html")
    print(f"\n✅ localhostでのアクセスのため、位置情報APIが動作します")
    print(f"   （HTTPSは不要）")
    print(f"\n終了: Ctrl+C を押してください\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 サーバーを停止しました")
