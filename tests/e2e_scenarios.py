"""End-to-end scenario verification script — run directly, not via pytest."""
import socket
import subprocess, sys, time, json, urllib.request, urllib.error


def _free_port() -> int:
    """Return an OS-allocated free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


PORT = _free_port()

proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'app.main:app',
     '--host', '127.0.0.1', '--port', str(PORT), '--log-level', 'error'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

# Wait until the server is actually accepting connections (up to 5 s)
for _ in range(25):
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
            break
    except OSError:
        time.sleep(0.2)

BASE = f'http://127.0.0.1:{PORT}'

def post(payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f'{BASE}/api/analyze', data=data,
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def get(path):
    try:
        with urllib.request.urlopen(f'{BASE}{path}', timeout=5) as r:
            return r.read().decode(), r.status
    except urllib.error.HTTPError as e:
        return e.read().decode(), e.code
    except Exception as e:
        return str(e), 0

results = {}
failures = []

# Health check
_, status = get('/api/health')
results['health'] = {'status': status, 'pass': status == 200}

# Homepage markers
body, status = get('/')
homepage_ok = all([
    'id="message"' in body,
    'id="url"' in body,
    'id="results"' in body,
    'id="url-inspections"' in body,
    'id="mlModelDetails"' in body,
    "Don't just read it." in body,
])
results['homepage'] = {'status': status, 'pass': status == 200 and homepage_ok}

# Scenario A: Fake internship with upfront fee
data, status = post({'message': 'Congratulations, you are shortlisted for an internship. Pay Rs.999 as a registration fee today to confirm your seat.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
results['A_fake_internship'] = {'level': level, 'status': status, 'pass': level in ['high', 'critical']}

# Scenario B: Account suspension + credential request + suspicious IP URL
data, status = post({'message': 'Your account will be blocked today. Verify your OTP at http://192.0.2.1/verify now.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
signals = [s['signal_id'] for s in data.get('signals', [])] if status == 200 else []
results['B_kyc_phishing'] = {'level': level, 'signals': signals, 'pass': level == 'critical'}

# Scenario C: UPI refund manipulation
data, status = post({'message': 'Your refund is pending. Scan the QR code and enter your UPI PIN to receive the amount.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
results['C_upi_refund'] = {'level': level, 'pass': level == 'critical'}

# Scenario D: Fake lottery + fee
data, status = post({'message': 'Congratulations! You have won a prize of Rs.5,00,000. Pay a processing fee of Rs.500 to claim your reward.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
results['D_fake_lottery'] = {'level': level, 'pass': level in ['high', 'critical']}

# Scenario E: Benign OTP warning (must NOT be high/critical)
data, status = post({'message': 'Security reminder: Never share your OTP, password, or UPI PIN with anyone. HDFC Bank.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
results['E_benign_otp_warning'] = {'level': level, 'pass': level in ['low_indicators', 'moderate']}

# Scenario F: Benign delivery message
data, status = post({'message': 'Your order #12345 will be delivered today by 6pm. Contact support if needed.', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
results['F_benign_delivery'] = {'level': level, 'pass': level in ['low_indicators', 'moderate']}

# Scenario G1: URL shortener
data, status = post({'message': 'Please review the offer at https://bit.ly/fake-offer123', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
url_signals = [s['signal_id'] for s in data.get('signals', [])] if status == 200 else []
results['G1_shortener_url'] = {'level': level, 'url_signals': url_signals, 'pass': 'url_shortener' in url_signals}

# Scenario G2: Raw IP host
data, status = post({'url': 'http://192.0.2.1/login', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
url_sigs = [s['signal_id'] for s in data.get('signals', [])] if status == 200 else []
results['G2_raw_ip'] = {'level': level, 'signals': url_sigs, 'pass': 'ip_address_host' in url_sigs}

# Scenario G3: Embedded credentials in URL
data, status = post({'url': 'https://user:pass@example.com/page', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
url_sigs = [s['signal_id'] for s in data.get('signals', [])] if status == 200 else []
results['G3_embedded_creds'] = {'level': level, 'signals': url_sigs, 'pass': 'embedded_url_credentials' in url_sigs}

# Scenario G4: Punycode host
data, status = post({'url': 'https://xn--pypal-4ve.com/signin', 'incident_status': 'received_only'})
level = data.get('assessment', {}).get('level', '?') if status == 200 else '?'
url_sigs = [s['signal_id'] for s in data.get('signals', [])] if status == 200 else []
results['G4_punycode'] = {'level': level, 'signals': url_sigs, 'pass': 'punycode_host' in url_sigs}

# Scenario G5: Malformed URL (not http/https)
data, status = post({'url': 'not-a-real-url', 'incident_status': 'received_only'})
results['G5_malformed_url'] = {'status': status, 'pass': status in [200, 422]}

# Scenario H: Empty input (must 422)
data, status = post({'message': '', 'incident_status': 'received_only'})
results['H_empty'] = {'status': status, 'pass': status == 422}

# Scenario I: Long input (9800 chars — within limit)
long_msg = 'Normal message text. ' * 468  # ~9828 chars
data, status = post({'message': long_msg, 'incident_status': 'received_only'})
results['I_long_input'] = {'status': status, 'pass': status == 200}

# Scenario I2: Over-limit input (10001 chars — must 422)
too_long = 'A' * 10001
data, status = post({'message': too_long, 'incident_status': 'received_only'})
results['I2_over_limit'] = {'status': status, 'pass': status == 422}

# Scenario J: ML model unavailability — check truthful state
data, status = post({'message': 'Simple test message.', 'incident_status': 'received_only'})
model = data.get('model', {}) if status == 200 else {}
results['J_model_state'] = {
    'available': model.get('available'),
    'status': model.get('status'),
    'has_limitation': bool(model.get('limitation')),
    'pass': status == 200 and model.get('status') in ['unavailable', 'available', 'not_run', 'error']
}

# Scenario L: Multiple URLs
data, status = post({'message': 'Check out https://bit.ly/abc and http://192.0.2.1/phish for more details.', 'incident_status': 'received_only'})
urls = data.get('urls', []) if status == 200 else []
results['L_multiple_urls'] = {
    'url_count': len(urls),
    'level': data.get('assessment', {}).get('level', '?') if status == 200 else '?',
    'pass': status == 200 and len(urls) == 2
}

proc.terminate()

# Summarize
passed = sum(1 for v in results.values() if v.get('pass'))
total = len(results)
print(f'\n=== SIFT E2E Scenario Results: {passed}/{total} passed ===\n')
for name, r in results.items():
    icon = 'PASS' if r.get('pass') else 'FAIL'
    extra = ''
    if 'level' in r:
        extra = f" level={r['level']}"
    elif 'status' in r:
        extra = f" http={r['status']}"
    if 'signals' in r:
        extra += f" signals={r['signals']}"
    print(f'  [{icon}] {name}{extra}')
