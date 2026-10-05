import os
import json
import requests
import warnings

# HTTPS sertifika uyarısını gizle
warnings.filterwarnings("ignore", message="Unverified HTTPS request")


# =========================================================
# TELEGRAM AYARLARI
# =========================================================

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


# =========================================================
# İLAN.GOV.TR API
# =========================================================

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
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json",
    "Origin": "https://www.ilan.gov.tr",
    "Referer": "https://www.ilan.gov.tr/",
    "Connection": "keep-alive"
}


# =========================================================
# SESSION OLUŞTUR
# =========================================================

session = requests.Session()
session.headers.update(headers)


# =========================================================
# ÖNCE ANA SİTEYİ TEST ET
# =========================================================

print("======================================")
print("ilan.gov.tr bağlantı testi başlıyor")
print("======================================")


test_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}


try:
    test = session.get(
        "https://www.ilan.gov.tr/",
        headers=test_headers,
        verify=False,
        timeout=60
    )

    print("ANA SİTE STATUS:", test.status_code)
    print(
        "ANA SİTE CONTENT TYPE:",
        test.headers.get("content-type")
    )
    print(
        "ANA SİTE CEVAP:",
        test.text[:500]
    )

except Exception as e:
    print("ANA SİTE TEST HATASI:", str(e))


print("======================================")
print("API isteği başlıyor")
print("======================================")


# =========================================================
# API İSTEĞİ
# =========================================================

try:
    r = session.post(
        url,
        json=payload,
        verify=False,
        timeout=60
    )

except Exception as e:
    raise Exception(
        f"ilan.gov.tr API bağlantı hatası: {e}"
    )


# =========================================================
# API CEVABINI KONTROL ET
# =========================================================

print(
    "ilan.gov.tr HTTP STATUS:",
    r.status_code
)

print(
    "ilan.gov.tr CONTENT TYPE:",
    r.headers.get("content-type")
)

print(
    "ilan.gov.tr RESPONSE:",
    r.text[:1000]
)


if r.status_code != 200:
    raise Exception(
        f"ilan.gov.tr HTTP hatası: {r.status_code}"
    )


# =========================================================
# JSON KONTROLÜ
# =========================================================

try:
    data = r.json()

except ValueError:
    raise Exception(
        "ilan.gov.tr JSON yerine farklı bir cevap döndürdü."
    )


# =========================================================
# İLANLARI AL
# =========================================================

ilanlar = []


try:
    ads = data["result"]["ads"]

except (KeyError, TypeError):
    print("API cevabının beklenen yapısı değişmiş olabilir.")
    print("Gelen JSON:")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])

    raise Exception(
        "ilan.gov.tr API cevabında 'result.ads' bulunamadı."
    )


for ilan in ads:

    ilan_no = ilan.get("adNo", "")
    baslik = ilan.get("title", "")
    kurum = ilan.get("advertiserName", "")

    uid = ilan_no

    ilanlar.append({
        "id": uid,
        "baslik": baslik,
        "kurum": kurum
    })


# =========================================================
# SEEN.JSON OKU
# =========================================================

try:

    with open(
        "seen.json",
        "r",
        encoding="utf-8"
    ) as f:

        seen = json.load(f)

except Exception:

    seen = {
        "ilanlar": []
    }


# =========================================================
# ESKİ İLANLAR
# =========================================================

eski = set(
    seen.get("ilanlar", [])
)


# =========================================================
# YENİ İLANLARI BUL
# =========================================================

yeni = []


for ilan in ilanlar:

    if ilan["id"] not in eski:

        yeni.append(ilan)


# =========================================================
# BİLGİLERİ YAZDIR
# =========================================================

print(
    "Toplam ilan:",
    len(ilanlar)
)

print(
    "Seen sayisi:",
    len(eski)
)

print(
    "Yeni ilan sayisi:",
    len(yeni)
)


# =========================================================
# TELEGRAM BİLDİRİMİ
# =========================================================

# İlk çalıştırmada eski ilanları Telegram'a göndermiyoruz.
# Sonraki çalıştırmalarda sadece yeni ilanlar gönderilir.

if eski:

    for ilan in yeni:

        telegram(
            f"🔔 Yeni İhale\n\n"
            f"{ilan['baslik']}\n\n"
            f"Kurum:\n{ilan['kurum']}\n\n"
            f"İlan No:\n{ilan['id']}\n\n"
            f"Kaynak:\nilan.gov.tr"
        )

        print(
            "Yeni ilan gönderildi:",
            ilan["baslik"]
        )


# =========================================================
# SEEN.JSON GÜNCELLE
# =========================================================

seen["ilanlar"] = [
    x["id"]
    for x in ilanlar
]


with open(
    "seen.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        seen,
        f,
        ensure_ascii=False,
        indent=2
    )


print("Tamamlandı")
