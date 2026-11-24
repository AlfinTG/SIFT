from fastapi.testclient import TestClient
from app.main import app

def test_frontend_integration():
    client = TestClient(app)

    # 1. Health check
    resp_health = client.get('/api/health')
    assert resp_health.status_code == 200
    assert resp_health.json() == {'status': 'ok', 'service': 'sift'}

    # 2. Static root check
    resp_root = client.get('/')
    assert resp_root.status_code == 200
    assert 'SIFT' in resp_root.text
    assert 'id="message"' in resp_root.text
    assert 'id="url"' in resp_root.text
    assert 'id="results"' in resp_root.text

    # 3. Static CSS / JS
    assert client.get('/styles.css').status_code == 200
    assert client.get('/app.js').status_code == 200

    # 4. Scan fake internship scenario
    resp_scan1 = client.post('/api/analyze', json={
        'message': 'Congratulations, you are shortlisted for an internship. Pay ₹799 as a registration fee today to confirm your seat.',
        'incident_status': 'received_only'
    })
    assert resp_scan1.status_code == 200
    d1 = resp_scan1.json()
    assert d1['assessment']['level'] == 'high'
    assert d1['assessment']['uncertain'] is True
    assert d1['model']['status'] == 'unavailable'
    assert len(d1['signals']) >= 1
    assert any(s['signal_id'] == 'upfront_job_fee' for s in d1['signals'])

    # 5. Scan UPI refund PIN scenario
    resp_scan2 = client.post('/api/analyze', json={
        'message': 'Your refund is pending. Scan the QR code and enter your UPI PIN immediately to receive the amount.',
        'incident_status': 'received_only'
    })
    assert resp_scan2.status_code == 200
    d2 = resp_scan2.json()
    assert d2['assessment']['level'] == 'critical'
    assert any(s['signal_id'] == 'credential_disclosure_request' for s in d2['signals'])

    # 6. Scan Legitimate OTP reminder
    resp_scan3 = client.post('/api/analyze', json={
        'message': 'Security reminder: Never share your OTP, password, or UPI PIN with anyone.',
        'incident_status': 'received_only'
    })
    assert resp_scan3.status_code == 200
    d3 = resp_scan3.json()
    assert d3['assessment']['level'] == 'low_indicators'
    assert d3['assessment']['uncertain'] is True

    # 7. Scan URL Shortener
    resp_scan4 = client.post('/api/analyze', json={
        'url': 'https://bit.ly/offer',
        'include_url_inspection': True
    })
    assert resp_scan4.status_code == 200
    d4 = resp_scan4.json()
    assert d4['assessment']['level'] == 'moderate'
    assert any(s['signal_id'] == 'url_shortener' for s in d4['signals'])

    # 8. Scan IP Host URL
    resp_scan5 = client.post('/api/analyze', json={
        'url': 'https://198.51.100.7/login',
        'include_url_inspection': True
    })
    assert resp_scan5.status_code == 200
    d5 = resp_scan5.json()
    assert d5['assessment']['level'] == 'moderate'
    assert any(s['signal_id'] == 'ip_address_host' for s in d5['signals'])

    # 9. Validation error check
    resp_val = client.post('/api/analyze', json={
        'message': '   ',
        'url': None
    })
    assert resp_val.status_code == 422
