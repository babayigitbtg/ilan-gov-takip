import requests
import urllib3

urllib3.disable_warnings()

url = "https://www.ilan.gov.tr/ilan/kategori/9/ihale-duyurulari?aci=62&txv=9&field=publish_time&order=desc"

r = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    verify=False,
    timeout=30
)

print("STATUS:", r.status_code)
print("=" * 80)
print(r.text[:5000])
