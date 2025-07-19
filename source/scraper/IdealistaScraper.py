import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from typing import List, Dict

class IdealistaScraper:
    def __init__(self, base_url: str = 'https://www.idealista.com/venta-viviendas/madrid-madrid/', pages: int = 1, output_file: str = 'idealista_listings.csv'):
        self.base_url = base_url
        self.pages = pages
        self.output_file = output_file
        self.headers_list = [
            # Varios user-agents para rotar
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'en-US,en;q=0.5'},
            {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'Accept-Language': 'en-US,en;q=0.5'},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)', 'Accept-Language': 'en-US,en;q=0.5'}
        ]
        self.properties = []

    def fetch_page(self, url: str) -> BeautifulSoup:
        try:
            headers = random.choice(self.headers_list)
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                print(f'Error al obtener {url} - Status Code: {response.status_code}')
                return None
        except requests.RequestException as e:
            print(f'Excepción durante el request: {e}')
            return None

    def parse_listing(self, listing) -> Dict:
        try:
            title = listing.find('a', class_='item-link')
            price = listing.find('span', class_='item-price')
            location = listing.find('span', class_='item-detail')
            features = listing.find_all('span', class_='item-detail')  # Puede haber varias

            return {
                'title': title.get_text(strip=True) if title else '',
                'price': price.get_text(strip=True) if price else '',
                'location': location.get_text(strip=True) if location else '',
                'details': ', '.join([f.get_text(strip=True) for f in features])
            }
        except Exception as e:
            print(f'Error al parsear una propiedad: {e}')
            return {}

    def scrape(self):
        for page in range(1, self.pages + 1):
            page_url = f"{self.base_url}pagina-{page}.htm" if page > 1 else self.base_url
            print(f"Scraping página: {page_url}")
            soup = self.fetch_page(page_url)
            if soup is None:
                continue

            listings = soup.find_all('article', class_='item')
            if not listings:
                print("No se encontraron propiedades en la página.")
                break

            for listing in listings:
                data = self.parse_listing(listing)
                if data:
                    self.properties.append(data)

            # Espera aleatoria para evitar bloqueo
            time.sleep(random.uniform(1.5, 3.0))

        self.save_to_csv()

    def save_to_csv(self):
        keys = ['title', 'price', 'location', 'details']
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for prop in self.properties:
                writer.writerow(prop)

        print(f"Datos guardados en {self.output_file}")

# Ejemplo de uso
if __name__ == "__main__":
    scraper = IdealistaScraper(
        base_url='https://www.idealista.com/venta-viviendas/madrid-madrid/',
        pages=3,  # Número de páginas que quieres scrapea
        output_file='./data/idealista_listings.csv'
    )
    scraper.scrape()
