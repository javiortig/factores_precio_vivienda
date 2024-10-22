"""
Este método puede ser limitante debido a las medidas de ciberseguridad que tiene idealista, ya que no permite hacer vairas peticiones 
de forma continuada. Quizá sería interesante utilizar proxies rotativos.
"""


import requests
from bs4 import BeautifulSoup
import csv


url = 'https://www.idealista.com/en/venta-viviendas/madrid-madrid/'

# Headers para imitar los requests de un browser normal
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'DNT': '1',
    'Referer': 'https://www.google.com/',  # imita a google
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'TE': 'Trailers',
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    listings = soup.find_all('article', class_='item')

    properties = []

     # Extrae cada propiedad
    for listing in listings:
        title = listing.find('a', class_='item-link').get_text(strip=True)
        price = listing.find('span', class_='item-price').get_text(strip=True)
        location = listing.find('span', class_='item-detail').get_text(strip=True)
        
        properties.append([title, price, location])
        
        print(f'Título: {title}')
        print(f'Precio: {price}')
        print(f'Localización: {location}')
        print('-' * 50)

    # Guarda los datos en un csv
    with open('./data/idealista_listings_generado.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['Title', 'Price', 'Location'])

        writer.writerows(properties)
else:
    print('Failed to retrieve the webpage. Status code:', response.status_code)
