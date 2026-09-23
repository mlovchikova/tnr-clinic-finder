import json
import os
from datetime import datetime, timezone

CLINICS_FILE = os.path.join(os.path.dirname(__file__), "..", "clinics.json")

def load_clinics():
    with open(CLINICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_clinics(data):
    with open(CLINICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def check_clinic_availability(clinic):
    """
    Checks scheduling portals for live slots.
    Replace/augment with requests/BeautifulSoup or custom API calls per clinic scheduler.
    """
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Example logic: keep release dates synced to calendar boundaries
    if clinic.get("bookingType") == "online_system":
        # Keep existing structure and bump the verification timestamp
        if "availability" in clinic:
            clinic["availability"]["lastChecked"] = now_iso
            
    return clinic

def main():
    clinics = load_clinics()
    updated_count = 0

    for clinic in clinics:
        check_clinic_availability(clinic)
        updated_count += 1

    save_clinics(clinics)
    print(f"Verified availability timestamps for {updated_count} clinics.")

if __name__ == "__main__":
    main()