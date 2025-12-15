#!/usr/bin/env python3
import http.server
import ssl
import os
import sys
import subprocess
from pathlib import Path

# カレントディレクトリを取得
os.chdir(Path(__file__).parent)

# HTTPサーバーハンドラー
handler = http.server.SimpleHTTPRequestHandler

# 自己署名証明書を生成
cert_file = 'cert.pem'
key_file = 'key.pem'

def create_self_signed_cert_with_openssl():
    """OpenSSLコマンドで証明書を生成"""
    try:
        # Windowsの場合、openssl.exeを探す
        openssl_paths = [
            r"C:\Program Files\Git\usr\bin\openssl.exe",
            r"C:\Program Files (x86)\Git\usr\bin\openssl.exe",
            r"C:\OpenSSL-Win64\bin\openssl.exe",
        ]
        
        openssl_cmd = None
        
        # 環境変数から探す
        result = subprocess.run(['where', 'openssl'], capture_output=True, text=True)
        if result.returncode == 0:
            openssl_cmd = result.stdout.strip().split('\n')[0]
        else:
            # 一般的なパスから探す
            for path in openssl_paths:
                if os.path.exists(path):
                    openssl_cmd = path
                    break
        
        if not openssl_cmd:
            return False
        
        # 証明書を生成（Windowsのコマンド形式に対応）
        cmd = f'"{openssl_cmd}" req -x509 -newkey rsa:2048 -keyout {key_file} -out {cert_file} -days 365 -nodes -subj "/CN=localhost"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"OpenSSL stderr: {result.stderr}")
            # 別のフォーマットで試す
            cmd = f'"{openssl_cmd}" req -x509 -newkey rsa:2048 -keyout {key_file} -out {cert_file} -days 365 -nodes -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return False
        
        print("✅ 自己署名証明書を作成しました")
        return True
        
    except Exception as e:
        print(f"OpenSSL エラー: {e}")
        return False

def create_self_signed_cert_with_python():
    """Pythonで証明書を生成（cryptography必要）"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import ipaddress
        from datetime import datetime, timedelta
        
        # 秘密鍵を生成
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # 証明書のサブジェクトとイシュアーを設定
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        # 証明書を構築
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"*.localhost"),
                x509.IPAddress(ipaddress.IPv4Address(u"127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # ファイルに保存
        with open(cert_file, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_file, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        print("✅ 自己署名証明書を作成しました")
        return True
        
    except ImportError:
        return False

# 証明書の確認・作成
if not os.path.exists(cert_file) or not os.path.exists(key_file):
    print("🔐 自己署名証明書を作成しています...")
    
    # OpenSSLで試す
    if not create_self_signed_cert_with_openssl():
        # Pythonで試す
        if not create_self_signed_cert_with_python():
            print("\n❌ 証明書作成に失敗しました")
            print("以下のいずれかをインストールしてください:")
            print("  1. OpenSSL: https://slproweb.com/products/Win32OpenSSL.html")
            print("  2. Python cryptography: pip install cryptography")
            sys.exit(1)

# SSLコンテキストを設定
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(cert_file, key_file)

# サーバー起動（ポート8443でHTTPS）
server = http.server.HTTPServer(('127.0.0.1', 8443), handler)
server.socket = context.wrap_socket(server.socket, server_side=True)

print("🚀 HTTPS サーバーが起動しました")
print("ブラウザで以下にアクセスしてください:")
print("https://localhost:8443/bike-parking-finder.html")
print("\n注意: 自己署名証明書を使用しているため、ブラウザに警告が表示されます")
print("      「詳細」→「〇〇にアクセス」をクリックして続行してください")
print("\nサーバーを終了: Ctrl+C")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n\nサーバーを停止しました")
