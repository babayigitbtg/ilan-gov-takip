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
"User-Agent": "Mozilla/5.0",
"Content-Type": "application/json"
}

r = requests.post(
url,
json=payload,
headers=headers,
verify=False,
timeout=60
)

data = r.json()

ilanlar = []

for ilan in data["result"]["ads"]:

```
ilan_no = ilan.get("adNo", "")
baslik = ilan.get("title", "")
kurum = ilan.get("advertiserName", "")

uid = ilan_no

ilanlar.append({
    "id": uid,
    "baslik": baslik,
    "kurum": kurum
})
```

try:
with open("seen.json", "r", encoding="utf-8") as f:
seen = json.load(f)
except:
seen = {"ilanlar": []}

eski = set(seen.get("ilanlar", []))

yeni = []

for ilan in ilanlar:

```
if ilan["id"] not in eski:

    yeni.append(ilan)
```

print("Toplam ilan:", len(ilanlar))
print("Seen sayisi:", len(eski))
print("Yeni ilan sayisi:", len(yeni))

if eski:

```
for ilan in yeni:

    telegram(
        f"🔔 Yeni İhale\n\n"
        f"{ilan['baslik']}\n\n"
        f"Kurum:\n{ilan['kurum']}\n\n"
        f"İlan No:\n{ilan['id']}\n\n"
        f"Kaynak:\nilan.gov.tr"
    )

    print("Yeni ilan gönderildi:", ilan["baslik"])
```

seen["ilanlar"] = [x["id"] for x in ilanlar]

with open("seen.json", "w", encoding="utf-8") as f:
json.dump(seen, f, ensure_ascii=False, indent=2)

print("Tamamlandı")
