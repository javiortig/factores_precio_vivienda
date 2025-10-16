import os
from .idealista_scraper import IdealistaScraper

def main():
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_folder, exist_ok=True)
    output_path = os.path.join(data_folder, 'idealista_listings.csv')

    scraper = IdealistaScraper(
        base_url='https://www.idealista.com/venta-viviendas/madrid-madrid/',
        pages=3,
        output_file=output_path,
        backend='requests',   # prueba 'playwright' si con requests recibes 403
        headless=True,
    )
    scraper.scrape()

if __name__ == "__main__":
    main()
