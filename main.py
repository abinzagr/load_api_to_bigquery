import requests
import json
import os
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

SERVICE_ACCOUNT_JSON = "thelio-apm-20250411-a83142d3955e.json" 

API_URL = "https://countriesnow.space/api/v0.1/countries/info?returns=population,capital,area"
PROJECT_ID = "thelio-apm-20250411"
DATASET_ID = "DTM_THELIO"
TABLE_ID = "COUNTRIES"
MAX_COUNTRIES = 150
SELECTED_COLUMNS = ["name", "cca2", "capital", "region", "population", "area"]

def fetch_country_data():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()

        if "application/json" not in response.headers.get("Content-Type", ""):
            raise ValueError("Réponse inattendue : pas du JSON")

        print("Aperçu des données brutes renvoyées par l'API :")
        print(response.text[:500])

        try:
            api_response = response.json()
            countries = api_response.get("data", [])
        except json.JSONDecodeError as e:
            with open("api_response_debug.json", "w") as debug_file:
                debug_file.write(response.text)
            raise ValueError(f"Erreur de parsing JSON : {e}")

        countries = countries[:MAX_COUNTRIES]
        cleaned_data = []

        for i, country in enumerate(countries):
            try:
                print(f"Traitement du pays {i + 1} : {country.get('name', 'Inconnu')}")

                cleaned_country = {
                    "name": country.get("name"),
                    "code": None,
                    "capital": country.get("capital"),
                    "region": None,
                    "population": country.get("population"),
                    "area": country.get("area"),
                }

                if cleaned_country["name"]:
                    cleaned_data.append(cleaned_country)
            except Exception as e:
                print(f"Erreur lors du nettoyage des données pour un pays : {e}")

        return cleaned_data

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête API : {e}")
    except ValueError as e:
        print(f"Erreur de traitement des données : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

    return []

def insert_data_into_bigquery_autodetect(data):
    try:
        client = bigquery.Client()

        table_ref = client.dataset(DATASET_ID).table(TABLE_ID)

        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            write_disposition="WRITE_TRUNCATE",
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        )

        job = client.load_table_from_json(data, table_ref, job_config=job_config)
        job.result()  # Bloque jusqu'à ce que le job soit fini

        print(f"{len(data)} lignes insérées dans {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")

    except DefaultCredentialsError:
        print("Erreur : Les identifiants Google Cloud ne sont pas configurés.")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans BigQuery : {e}")
        
def main():
    data = fetch_country_data()
    if data:
        insert_data_into_bigquery_autodetect(data)
    else:
        print("Aucune donnée à insérer dans BigQuery.")

if __name__ == "__main__":
    main()
