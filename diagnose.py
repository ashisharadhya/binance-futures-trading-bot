import hashlib
import hmac
import os
import time
import requests

API_KEY = os.environ.get("BINANCE_TESTNET_API_KEY")
API_SECRET = os.environ.get("BINANCE_TESTNET_API_SECRET")

BASE_URL = "https://demo-fapi.binance.com"

print("=" * 60)
print("STEP 1: Checking environment variables are set")
print("=" * 60)
if not API_KEY or not API_SECRET:
    print("FAIL: BINANCE_TESTNET_API_KEY or BINANCE_TESTNET_API_SECRET is not set.")
    raise SystemExit(1)
print(f"API_KEY starts with: {API_KEY[:8]}... (length {len(API_KEY)})")
print(f"API_SECRET starts with: {API_SECRET[:8]}... (length {len(API_SECRET)})")

print()
print("=" * 60)
print("STEP 2: Public endpoint (no auth needed)")
print("=" * 60)
try:
    r = requests.get(f"{BASE_URL}/fapi/v1/time", timeout=10)
    print(f"Status code: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"FAIL: could not reach {BASE_URL} at all: {e}")
    raise SystemExit(1)

print()
print("=" * 60)
print("STEP 3: Authenticated endpoint - account balance")
print("=" * 60)

timestamp = int(time.time() * 1000)
query_string = f"timestamp={timestamp}"
signature = hmac.new(
    API_SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
).hexdigest()

url = f"{BASE_URL}/fapi/v2/balance?{query_string}&signature={signature}"
headers = {"X-MBX-APIKEY": API_KEY}

r = requests.get(url, headers=headers, timeout=10)
print(f"Status code: {r.status_code}")
print(f"Response: {r.text}")

print()
print("=" * 60)
if r.status_code == 200:
    print("SUCCESS: key works against demo-fapi.binance.com")
else:
    print("Still failing — see exact error above.")
print("=" * 60)
