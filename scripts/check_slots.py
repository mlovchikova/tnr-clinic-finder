import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timezone

CLINICS_FILE = os.path.join(os.path.dirname(__file__), "..", "clinics.json")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")  # Set in GitHub Repository Secrets

def load_clinics():
    with open(CLINICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_clinics(data):
    with open(CLINICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def fetch_latest_facebook_post(page_id_or_handle):
    """
    Fetches the latest post using Meta Graph API:
    https://graph.facebook.com/v19.0/{page-id}/posts?fields=message,created_time,permalink_url&limit=1
    """
    if not FB_ACCESS_TOKEN or not page_id_or_handle:
        return None

    try:
        url = f"https://graph.facebook.com/v19.0/{urllib.parse.quote(page_id_or_handle)}/posts?fields=message,created_time,permalink_url&limit=1&access_token={FB_ACCESS_TOKEN}"
        req = urllib.request.Request(url, headers={"User-Agent": "TNRFinderBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                payload = json.loads(response.read().decode())
                data = payload.get("data", [])
                if data:
                    post = data[0]
                    # Truncate post message if excessively long
                    raw_msg = post.get("message", "Recent update on Facebook page.")
                    truncated_msg = raw_msg[:240] + ("..." if len(raw_msg) > 240 else "")
                    return {
                        "text": truncated_msg,
                        "postedAt": post.get("created_time"),
                        "postUrl": post.get("permalink_url")
                    }
    except Exception as e:
        print(f"Facebook Graph API notice for {page_id_or_handle}: {e}")
    return None

def check_clinic(clinic):
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 1. Update availability timestamp
    if "availability" in clinic and clinic["availability"]:
        clinic["availability"]["lastChecked"] = now_iso

    # 2. Update Facebook feed if configured
    fb_config = clinic.get("facebook")
    if fb_config and fb_config.get("pageId"):
        new_post = fetch_latest_facebook_post(fb_config["pageId"])
        if new_post:
            clinic["facebook"]["latestPost"] = new_post

    return clinic

def main():
    clinics = load_clinics()
    for clinic in clinics:
        check_clinic(clinic)

    save_clinics(clinics)
    print("Clinics updated successfully.")

if __name__ == "__main__":
    main()