import requests
import os

def main():
    url = 'https://rsf.org/sites/default/files/import_classement/2025.csv'
    os.makedirs('data/raw/trust_score', exist_ok=True)
    response = requests.get(url)
    output_path = 'data/raw/trust_score/country_2025.csv'
    with open(output_path, 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    main()