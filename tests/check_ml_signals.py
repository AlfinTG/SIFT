"""Check ML signal presence across all demo scenarios."""
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
scenarios = [
    'Congratulations, you are shortlisted for an internship. Pay Rs.799 as a registration fee today to confirm your seat.',
    'Your refund is pending. Scan the QR code and enter your UPI PIN immediately to receive the amount.',
    'Your account will be suspended today. Reply with your OTP to complete your KYC.',
    'You are a prize winner. Pay a processing fee today to release your reward.',
    'Security reminder: Never share your OTP, password, or UPI PIN with anyone.',
    'Payment confirmation: Rs.799 was received successfully. Keep this receipt for your records.',
    'Your parcel has been delivered. View its status in the delivery app you normally use.',
    'We noticed a sign-in to your account. Review activity in the official app, and never share your OTP.',
    'Please review the offer at https://bit.ly/offer.',
    'Review https://198.51.100.7/login before continuing.',
]
for msg in scenarios:
    r = client.post('/api/analyze', json={'message': msg})
    b = r.json()
    sources = set(s['source'] for s in b['signals'])
    ml = b['model']
    level = b['assessment']['level']
    pred = ml.get('prediction')
    avail = ml.get('available')
    print(f'  level={level} sources={sources} avail={avail} pred={pred}')
    print(f'    {msg[:70]}')
