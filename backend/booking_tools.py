import json, os
from dateutil.parser import isoparse

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def _load_json(name):
    with open(os.path.join(DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)

CABINS = _load_json("cabins.json")
RATES = _load_json("rates.json")
AVAIL = _load_json("availability.json")

def _date_range_overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

def check_availability(checkin: str, checkout: str, guests: int, cabin_type=None, pets=False):
    ci = isoparse(checkin).date()
    co = isoparse(checkout).date()

    candidates = CABINS
    if cabin_type:
        candidates = [c for c in candidates if c["type"] == cabin_type]
    candidates = [c for c in candidates if c["max_guests"] >= guests]
    if pets:
        candidates = [c for c in candidates if c["pet_friendly"]]

    available = []
    for c in candidates:
        booked = AVAIL.get(c["cabin_id"], [])
        conflict = False
        for b in booked:
            b_ci = isoparse(b["checkin"]).date()
            b_co = isoparse(b["checkout"]).date()
            if _date_range_overlap(ci, co, b_ci, b_co):
                conflict = True
                break
        if not conflict:
            available.append(c)

    return available

def quote_price(checkin: str, checkout: str, cabin_type: str, pets=False, num_pets=0):
    ci = isoparse(checkin).date()
    co = isoparse(checkout).date()
    nights = (co - ci).days
    if nights <= 0:
        raise ValueError("Checkout must be after checkin")

    total_nightly = 0
    d = ci
    while d < co:
        is_weekend = d.weekday() in (4, 5)  # Fri/Sat
        rate = RATES[cabin_type]["weekend"] if is_weekend else RATES[cabin_type]["weekday"]
        total_nightly += rate
        d = d.fromordinal(d.toordinal() + 1)

    cleaning = RATES["fees"]["cleaning"]
    service = RATES["fees"]["service"]
    pet_fee = (RATES["pet_fee_per_night"] * nights * max(num_pets, 0)) if pets else 0

    subtotal = total_nightly + cleaning + service + pet_fee
    tax = subtotal * RATES["fees"]["tax_rate"]
    total = subtotal + tax

    return {
        "nights": nights,
        "nightly_total": round(total_nightly, 2),
        "cleaning_fee": cleaning,
        "service_fee": service,
        "pet_fee": pet_fee,
        "tax": round(tax, 2),
        "total": round(total, 2)
    }

def create_booking_link(checkin: str, checkout: str, cabin_id: str, guests: int):
    return f"https://demo-booking.local/checkout?cabin={cabin_id}&checkin={checkin}&checkout={checkout}&guests={guests}"
