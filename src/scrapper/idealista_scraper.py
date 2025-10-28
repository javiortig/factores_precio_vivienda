# idealista_scraper.py
from __future__ import annotations
import csv
import random
import re
import time
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class IdealistaScraper:
    """
    Scraper para listados de Idealista (venta).
    - Backend "requests" (por defecto) con sesión, headers y backoff 403/429.
    - Backend "playwright" (opcional) para páginas con JS/anti-bot.

    Extrae por anuncio:
      zona, ciudad, calle, precio, num_habitaciones, superficie_m2,
      garaje (bool), descripcion, tipo_vivienda, id, url
    """

    def __init__(
        self,
        base_url: str = "https://www.idealista.com/venta-viviendas/madrid-madrid/",
        pages: int = 1,
        output_file: str = "./data/demo/idealista_listings.csv",
        backend: str = "requests",  # "requests" | "playwright"
        headless: bool = True,
        min_delay: float = 2.0,
        max_delay: float = 4.0,
    ):
        self.base_url = base_url.rstrip("/") + "/"
        self.pages = int(pages)
        self.output_file = output_file
        self.backend = backend.lower()
        self.headless = headless
        self.min_delay = float(min_delay)
        self.max_delay = float(max_delay)

        self.properties: List[Dict[str, str]] = []

        # --- Sesión y cabeceras tipo navegador para requests ---
        self.session: Optional[requests.Session] = None
        self.common_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                "image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": "https://www.idealista.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }

        if self.backend not in {"requests", "playwright"}:
            raise ValueError("backend debe ser 'requests' o 'playwright'")

        if self.backend == "requests":
            self.session = requests.Session()

    # ------------------ Utilidades ------------------

    @staticmethod
    def _sleep_jitter(min_s: float, max_s: float) -> None:
        time.sleep(random.uniform(min_s, max_s))

    @staticmethod
    def _clean_text(t: Optional[str]) -> str:
        if not t:
            return ""
        return re.sub(r"\s+", " ", t).strip()

    # Heurística simple para detectar 'garaje' en detalles/descripcion
    @staticmethod
    def _has_garage(*texts: str) -> bool:
        hay = " ".join(t for t in texts if t).lower()
        keywords = [
            "garaje", "plaza de garaje", "plaza garaje",
            "parking", "aparcamiento", "plaza de parking",
        ]
        return any(k in hay for k in keywords)

    # Parsear título tipo: "Piso en Calle X, Barrio, Madrid"
    @staticmethod
    def _parse_title(title: str) -> Dict[str, str]:
        res = {"tipo_vivienda": "", "calle": "", "zona": "", "ciudad": ""}

        t = title.strip()
        if not t:
            return res

        # Separar por " en " (la parte antes es el tipo de vivienda, que puede ser multi-palabra)
        m = re.split(r"\s+en\s+", t, maxsplit=1, flags=re.IGNORECASE)
        if len(m) == 2:
            res["tipo_vivienda"] = m[0].strip()
            resto = m[1].strip()
        else:
            # Si no está "en", intenta captar el primer token como tipo
            parts = t.split(",", 1)
            res["tipo_vivienda"] = parts[0].strip()
            resto = parts[1].strip() if len(parts) > 1 else ""

        if resto:
            tokens = [s.strip() for s in resto.split(",") if s.strip()]
            # Heurística:
            # - último token: ciudad
            # - penúltimo: zona (barrio/distrito) si existe
            # - lo demás: calle (puede contener comas)
            if len(tokens) >= 1:
                res["ciudad"] = tokens[-1]
            if len(tokens) >= 2:
                res["zona"] = tokens[-2]
            if len(tokens) >= 3:
                res["calle"] = ", ".join(tokens[:-2])
            elif len(tokens) == 2:
                res["calle"] = tokens[0]
            elif len(tokens) == 1:
                # sólo ciudad; calle/zona se quedan vacías
                pass

        # Normaliza tipo (opcional, sin forzar demasiado)
        res["tipo_vivienda"] = res["tipo_vivienda"].lower().capitalize()

        return res

    # ------------------ Backend requests ------------------

    def _warmup_requests(self) -> None:
        """Visita la home para obtener cookies (consent/CF)."""
        assert self.session is not None
        try:
            self.session.get(
                "https://www.idealista.com/",
                headers=self.common_headers,
                timeout=15,
            )
        except requests.RequestException as e:
            print(f"[warmup] Excepción: {e}")
        self._sleep_jitter(1.0, 2.0)

    def _fetch_page_requests(self, url: str) -> Optional[BeautifulSoup]:
        """Obtiene y parsea con backoff ante 403/429."""
        assert self.session is not None
        try:
            for attempt in range(4):
                r = self.session.get(url, headers=self.common_headers, timeout=25)
                if r.status_code == 200:
                    return BeautifulSoup(r.content, "html.parser")
                if r.status_code in (403, 429):
                    wait = 2 ** attempt + random.random()
                    print(f"[requests] {r.status_code} en {url}. Reintento en {wait:.1f}s…")
                    time.sleep(wait)
                    continue
                print(f"[requests] HTTP {r.status_code} en {url}")
                return None
        except requests.RequestException as e:
            print(f"[requests] Excepción: {e}")
        return None

    # ------------------ Backend Playwright ------------------

    def _fetch_page_playwright(self, url: str) -> Optional[BeautifulSoup]:
        """Usa Playwright (Chromium) para obtener HTML ejecutando JS."""
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            print("[playwright] No disponible. Instálalo con: pip install playwright && playwright install")
            print(f"[playwright] Detalle: {e}")
            return None

        html = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                ctx = browser.new_context(locale="es-ES")
                page = ctx.new_page()
                page.set_extra_http_headers({"Accept-Language": "es-ES,es;q=0.9,en;q=0.8"})

                page.goto("https://www.idealista.com/", wait_until="domcontentloaded", timeout=60000)
                self._sleep_jitter(1.0, 2.0)

                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                # page.wait_for_selector("article", timeout=10000)  # si lo necesitas
                self._sleep_jitter(1.0, 2.0)

                html = page.content()
                browser.close()
        except Exception as e:
            print(f"[playwright] Excepción: {e}")
            return None

        if html:
            return BeautifulSoup(html, "html.parser")
        return None

    # ------------------ Parsing ------------------

    def parse_listing(self, listing) -> Dict[str, str]:
        """
        Extrae:
          zona, ciudad, calle, precio, num_habitaciones, superficie_m2,
          garaje (bool), descripcion, tipo_vivienda, id, url
        """
        try:
            # id anuncio
            ad_id = listing.get("data-element-id") or listing.get("data-adid") or ""

            # Título y URL
            a = listing.select_one("a.item-link, a.item-link--title, a[href*='/inmueble/']")
            title = self._clean_text(a.get_text()) if a else ""
            url = ""
            if a and a.get("href"):
                href = a.get("href")
                url = href if href.startswith("http") else f"https://www.idealista.com{href}"

            # Precio
            price_el = listing.select_one("span.item-price, span.price, div.item-price, .price-row .item-price")
            precio = self._clean_text(price_el.get_text()) if price_el else ""

            # Detalles rápidos (habitaciones, m2, etc.)
            details_container = listing.select_one(".item-detail-char, .item-details, .item-info")
            detail_texts: List[str] = []
            if details_container:
                for s in details_container.select("span.item-detail, li.item-detail, span.char, li.char"):
                    txt = self._clean_text(s.get_text())
                    if txt:
                        detail_texts.append(txt)
            details_joined = ", ".join(detail_texts)

            # habitaciones
            num_hab = ""
            m_hab = re.search(r"(\d+)\s*hab", details_joined, flags=re.IGNORECASE)
            if m_hab:
                num_hab = m_hab.group(1)

            # superficie
            superficie_m2 = ""
            m_m2 = re.search(r"(\d+(?:[.,]\d+)?)\s*m²", details_joined, flags=re.IGNORECASE)
            if m_m2:
                superficie_m2 = m_m2.group(1).replace(",", ".")

            # Descripción
            desc_el = listing.select_one("div.item-description p, div.item-description, .description p")
            descripcion = self._clean_text(desc_el.get_text()) if desc_el else ""

            # Garaje (heurística por palabras clave en detalles + descripción)
            garaje = self._has_garage(details_joined, descripcion)

            # Tipo, calle, zona, ciudad desde el título
            tparts = self._parse_title(title)
            tipo_vivienda = tparts.get("tipo_vivienda", "")
            calle = tparts.get("calle", "")
            zona = tparts.get("zona", "")
            ciudad = tparts.get("ciudad", "")

            return {
                "id": ad_id,
                "tipo_vivienda": tipo_vivienda,
                "calle": calle,
                "zona": zona,
                "ciudad": ciudad,
                "precio": precio,
                "num_habitaciones": num_hab,
                "superficie_m2": superficie_m2,
                "garaje": str(bool(garaje)),
                "descripcion": descripcion,
                "url": url,
            }
        except Exception as e:
            print(f"[parse] Error: {e}")
            return {}

    # ------------------ Flujo principal ------------------

    def _page_url(self, page: int) -> str:
        return f"{self.base_url}pagina-{page}.htm" if page > 1 else self.base_url

    def fetch_soup(self, url: str) -> Optional[BeautifulSoup]:
        if self.backend == "requests":
            if not hasattr(self, "_did_warmup"):
                self._warmup_requests()
                self._did_warmup = True
            return self._fetch_page_requests(url)
        else:
            return self._fetch_page_playwright(url)

    def scrape(self) -> None:
        print(f"[scraper] Inicio | backend={self.backend} | páginas={self.pages}")
        for page_num in range(1, self.pages + 1):
            url = self._page_url(page_num)
            print(f"[scraper] Página {page_num}: {url}")

            soup = self.fetch_soup(url)
            if not soup:
                print("[scraper] No se pudo obtener la página, continúo…")
                continue

            # Selectores amplios para artículos (cambian a menudo)
            articles = soup.select("article.item, article.item-multimedia-container, article")
            if not articles:
                print("[scraper] No se encontraron artículos en la página.")
            else:
                for art in articles:
                    data = self.parse_listing(art)
                    if data and any(data.values()):
                        self.properties.append(data)

            self._sleep_jitter(self.min_delay, self.max_delay)

        self.save_to_csv()
        print(f"[scraper] Fin. Total propiedades: {len(self.properties)}")

    # ------------------ Persistencia ------------------

    def save_to_csv(self) -> None:
        if not self.properties:
            print("[csv] No hay datos que guardar.")
            return
        keys = [
            "id", "tipo_vivienda", "calle", "zona", "ciudad",
            "precio", "num_habitaciones", "superficie_m2",
            "garaje", "descripcion", "url",
        ]
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for prop in self.properties:
                writer.writerow({k: prop.get(k, "") for k in keys})
        print(f"[csv] Guardado en {self.output_file}")
