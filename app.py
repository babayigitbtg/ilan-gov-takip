import os
import json
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def telegram(msg):
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


url = "https://www.ilan.gov.tr/api/api/services/app/Ad/AdsByFilter"

payload = {
    "keys": {
        "aci": [62],
        "txv": [9],
        "order": ["desc"],
        "field": ["publish_time"]
    },
    "sorting": "publish_time desc",
    "skipCount": 0,
    "maxResultCount": 50
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://www.ilan.gov.tr/",
    "Origin": "https://www.ilan.gov.tr"
}

r = requests.post(
    url,
    json=payload,
    headers=headers,
    verify=False,
    timeout=60
)

print("ilan.gov.tr HTTP STATUS:", r.status_code)
print("ilan.gov.tr CONTENT TYPE:", r.headers.get("content-type"))
print("ilan.gov.tr RESPONSE:", r.text[:1000])

if r.status_code != 200:
    raise Exception(
        f"ilan.gov.tr HTTP hatası: {r.status_code}"
    )

try:
    data = r.json()
except ValueError:
    raise Exception(
        "ilan.gov.tr JSON yerine farklı bir cevap döndürdü."
    )

ilanlar = []

for ilan in data["result"]["ads"]:
    ilan_no = ilan.get("adNo", "")
    baslik = ilan.get("title", "")
    kurum = ilan.get("advertiserName", "")

    uid = ilan_no

    ilanlar.append({
        "id": uid,
        "baslik": baslik,
        "kurum": kurum
    })

try:
    with open("seen.json", "r", encoding="utf-8") as f:
        seen = json.load(f)
except:
    seen = {"ilanlar": []}

eski = set(seen.get("ilanlar", []))

yeni = []

for ilan in ilanlar:
    if ilan["id"] not in eski:
        yeni.append(ilan)

print("Toplam ilan:", len(ilanlar))
print("Seen sayisi:", len(eski))
print("Yeni ilan sayisi:", len(yeni))

if eski:
    for ilan in yeni:
        telegram(
            f"🔔 Yeni İhale\n\n"
            f"{ilan['baslik']}\n\n"
            f"Kurum:\n{ilan['kurum']}\n\n"
            f"İlan No:\n{ilan['id']}\n\n"
            f"Kaynak:\nilan.gov.tr"
        )

        print("Yeni ilan gönderildi:", ilan["baslik"])

seen["ilanlar"] = [x["id"] for x in ilanlar]

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump(seen, f, ensure_ascii=False, indent=2)

print("Tamamlandı")
