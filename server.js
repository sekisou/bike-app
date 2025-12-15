// Node.js簡易HTTPSサーバー
const https = require('https');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const port = 8443;
const dir = __dirname;

// 自己署名証明書を作成する関数
function generateSelfSignedCert() {
    const cert = path.join(dir, 'cert.pem');
    const key = path.join(dir, 'key.pem');
    
    if (fs.existsSync(cert) && fs.existsSync(key)) {
        return { cert, key };
    }
    
    console.log('自己署名証明書を生成しています...');
    const { exec } = require('child_process');
    const cmd = `openssl req -x509 -newkey rsa:2048 -keyout "${key}" -out "${cert}" -days 365 -nodes -subj "/CN=localhost"`;
    
    try {
        exec(cmd, (error) => {
            if (error) {
                console.error('証明書生成エラー:', error);
                process.exit(1);
            }
            console.log('✅ 証明書を生成しました');
        });
    } catch (e) {
        console.error('OpenSSLが見つかりません。Pythonサーバーをご利用ください。');
        process.exit(1);
    }
    
    return { cert, key };
}

// 簡易ファイルサーバー
function requestHandler(req, res) {
    let filePath = path.join(dir, req.url === '/' ? 'bike-parking-finder.html' : req.url);
    
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404);
            res.end('ファイルが見つかりません');
            return;
        }
        
        let contentType = 'text/html';
        if (filePath.endsWith('.css')) contentType = 'text/css';
        else if (filePath.endsWith('.js')) contentType = 'application/javascript';
        
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
}

try {
    const { cert, key } = generateSelfSignedCert();
    
    const options = {
        key: fs.readFileSync(key),
        cert: fs.readFileSync(cert)
    };
    
    const server = https.createServer(options, requestHandler);
    
    server.listen(port, () => {
        console.log('\n🚀 HTTPS サーバーが起動しました');
        console.log(`📍 ブラウザで以下にアクセスしてください:`);
        console.log(`   https://localhost:${port}/bike-parking-finder.html`);
        console.log('\n⚠️  注意: 自己署名証明書を使用しているため、以下の手順で進めてください:');
        console.log('   1. ブラウザに警告が表示されます');
        console.log('   2. 「詳細」をクリック');
        console.log('   3. 「localhost にアクセス（安全でありません）」をクリック');
        console.log('\n終了: Ctrl+C を押してください\n');
    });
    
} catch (err) {
    console.error('サーバー起動エラー:', err);
    console.log('\n💡 代わりにPythonサーバーを使用してください:');
    console.log('   python server.py');
}
