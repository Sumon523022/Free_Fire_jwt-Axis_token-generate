import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.protobuf.json_format import MessageToDict
import WishListLeaderboard_pb2

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

REGION_BASE_URLS = {
    "IND": "https://client.ind.freefiremobile.com",
    "BD": "https://clientbp.ggpolarbear.com",
    "PK": "https://clientbp.ggpolarbear.com",
    "SG": "https://clientbp.ggpolarbear.com",
    "ID": "https://clientbp.ggpolarbear.com",
    "ME": "https://clientbp.ggpolarbear.com",
    "VN": "https://clientbp.ggpolarbear.com",
    "TH": "https://clientbp.ggpolarbear.com",
    "TW": "https://clientbp.ggpolarbear.com",
    "EUROPE": "https://clientbp.ggpolarbear.com",
    "RU": "https://clientbp.ggpolarbear.com",
    "BR": "https://client.us.freefiremobile.com",
    "US": "https://client.us.freefiremobile.com",
    "NA": "https://client.us.freefiremobile.com",
    "SAC": "https://client.us.freefiremobile.com",
}

CREDENTIALS = {
    "IND": {"uid": "6196721019", "password": "ADI_qCI7bb"},
    "ME": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "BD": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "PK": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "ID": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "TH": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "BR": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "RU": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "TW": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "SG": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "VN": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "EUROPE": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "US": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "NA": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
    "SAC": {"uid": "YOUR_UID_HERE", "password": "YOUR_PASSWORD_HERE"},
}

FIXED_PAYLOAD = bytes.fromhex("1a725b2c56ec52ba7d09623454c0a003")
RAIGEN_JWT_API = "https://freefiremax.pages.dev/GenJwt/token?key=raigenff&uid={uid}&password={password}"
ITEM_INFO_API = "https://ff-item-info.vercel.app/info?item_id={item_id}"
GAME_HEADERS = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-S908E Build/TP1A.220624.014)",
    "X-GA": "v1 1",
    "X-Unity-Version": "2018.4.11f1",
    "ReleaseVersion": "OB55",
    "Content-Type": "application/octet-stream",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
}

def fetch_item_info(item_id):
    try:
        resp = requests.get(ITEM_INFO_API.format(item_id=item_id), timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def process_one_item(item):
    item_id = str(item.get('id', ''))
    rank = int(item.get('rank', 0))
    trend = int(item.get('trend', 0))

    info = fetch_item_info(item_id)
    return {
        "rank": rank,
        "trend": trend,
        "name": info.get("name", "Unknown") if info else "Unknown",
        "item_id": item_id,
        "type": info.get("type", "Unknown") if info else "Unknown"
    }

def process_items_parallel(raw_items):
    result = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_item = {executor.submit(process_one_item, item): item for item in raw_items}
        for future in as_completed(future_to_item):
            result.append(future.result())
    result.sort(key=lambda x: x["rank"])
    return result

@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def api_docs():
    return jsonify({
        "service": "Free Fire Wishlist Leaderboard API",
        "version": "3.2",
        "endpoints": {
            "/token": {
                "description": "Fetch wishlist leaderboard data (weekly/monthly) with item info.",
                "parameters": {
                    "region": "Region code (default: IND). Available: IND, BD, PK, SG, ID, ME, VN, TH, TW, EUROPE, RU, BR, US, NA, SAC",
                    "type": "Data filter: all (default), weekly, monthly"
                },
                "example": "/token?uid={uid}&password={encoded_password}"
            }
        }
    }), 200

@app.route('/token', methods=['GET'])
def leaderboard():
    region = request.args.get('region', 'IND').upper()
    if region not in REGION_BASE_URLS:
        return jsonify({"status": "error", "message": f"Invalid region: {region}"}), 400

    base_url = REGION_BASE_URLS[region]
    creds = CREDENTIALS.get(region)
    if not creds or creds["uid"] == "YOUR_UID_HERE" or creds["password"] == "YOUR_PASSWORD_HERE":
        return jsonify({"status": "error", "message": f"Credentials not configured for region {region}"}), 500

    type_filter = request.args.get('type', 'all').lower()
    if type_filter not in ('all', 'weekly', 'monthly'):
        return jsonify({"status": "error", "message": "type must be all, weekly, or monthly."}), 400

    try:
        jwt_url = RAIGEN_JWT_API.format(uid=creds["uid"], password=creds["password"])
        jwt_resp = requests.get(jwt_url, timeout=10)
        if jwt_resp.status_code != 200:
            return jsonify({"status": "error", "message": "Failed to generate JWT."}), 500
        jwt_data = jwt_resp.json()
        token = jwt_data.get("token")
        if not token:
            return jsonify({"status": "error", "message": "No token in Raigen response."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"JWT generation failed: {str(e)}"}), 500

    headers = GAME_HEADERS.copy()
    headers['Authorization'] = f"Bearer {token}"

    try:
        url = f"{base_url}/GetWishListLeaderboard"
        resp = requests.post(url, headers=headers, data=FIXED_PAYLOAD, timeout=15, verify=False)
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"Game server returned {resp.status_code}"}), 500

        lb = WishListLeaderboard_pb2.LeaderboardResponse()
        lb.ParseFromString(resp.content)
        lb_dict = MessageToDict(lb, preserving_proto_field_name=False)

        weekly_raw = lb_dict.get('weekly', [])
        monthly_raw = lb_dict.get('monthly', [])

        weekly = process_items_parallel(weekly_raw)
        monthly = process_items_parallel(monthly_raw)

        response = {"region": region}
        if type_filter in ('all', 'weekly'):
            response["weekly"] = weekly
        if type_filter in ('all', 'monthly'):
            response["monthly"] = monthly

        return jsonify(response)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
