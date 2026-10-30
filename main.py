import requests

url = "https://www.federalregister.gov/api/v1/documents.json"

params = {
    "conditions[publication_date][gte]": "2021-01-01",
    "conditions[publication_date][lte]": "2025-12-31",
    "conditions[type][]": ["RULE", "PRORULE"],
    "per_page": 1000,
    "order": "newest"
}

response = requests.get(url, params=params)
data = response.json()

print("Total documents:", data["count"])
print("Documents retrieved:", len(data["results"]))
print(data["results"][0]["title"])