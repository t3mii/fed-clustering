import pandas as pd
import time
import requests
from datetime import date
from calendar import monthrange
def retrieve_documents():
    url = "https://www.federalregister.gov/api/v1/documents.json"

    all_documents = []

    for year in range(2021, 2026):
        for month in range(1, 13):

            start_date = date(year, month, 1)
            end_date = date(
                year,
                month,
                monthrange(year, month)[1]
            )

            params = {
                "conditions[publication_date][gte]": start_date.isoformat(),
                "conditions[publication_date][lte]": end_date.isoformat(),
                "conditions[type][]": ["RULE", "PRORULE"],
                "per_page": 1000,
                "order": "newest"
            }

            page = 1

            while True:
                params["page"] = page

                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()
                results = data.get("results", [])

                if not results:
                    break

                all_documents.extend(results)

                total_pages = data.get("total_pages", 1)

                if page >= total_pages:
                    break

                page += 1

            print(
                f"Completed {year}-{month:02d}: "
                f"{len(all_documents)} documents collected so far"
            ) #just so I can know what is being done

            time.sleep(0.2) #leave some requests gaps

    df = pd.DataFrame(all_documents)

    df = df.drop_duplicates(subset="document_number")

    df.to_csv("federal_register_documents.csv", index=False)

    print("Total unique documents:", len(df))
    print(df[["document_number", "title", "publication_date"]].head())
    df.to_csv("data/federal_register_documents.csv", index=False)


if __name__ == "__main__":
    retrieve_documents()