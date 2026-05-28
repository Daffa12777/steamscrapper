import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

SEARCH_FILTERS = ['topsellers', 'mostplayed', 'newreleases', 'upcomingreleases']
MAX_PER_FILTER = 300


def get_total_pages(doc):
    """Extract total page count from a parsed page."""
    pagination = doc.find('div', {'class': 'search_pagination_right'})
    if not pagination:
        return 1
    page_links = pagination.find_all('a')
    if len(page_links) < 2:
        return 1
    try:
        return int(page_links[-2].text)
    except (ValueError, IndexError):
        return 1


def find_game_containers(doc):
    candidates = [
        ('div', 'responsive_search_name_combined'),
        ('a',   'search_result_row'),
    ]
    for tag, cls in candidates:
        items = doc.find_all(tag, {'class': cls})
        if items:
            return items, cls
    return [], None


def parse_price_value(price_str):
    """
    Coba ekstrak nilai numerik dari string harga (misal '$9.99' -> 9.99).
    Mengembalikan float atau None jika tidak bisa di-parse.
    """
    if not price_str or price_str in ('N/A', 'Free', 'Free To Play'):
        return None
    cleaned = re.sub(r'[^\d.,]', '', price_str).replace(',', '.')
    # Ambil angka terakhir jika ada beberapa titik (misal '1.299.99' -> ambil bagian valid)
    match = re.search(r'\d+(?:\.\d+)?', cleaned)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def calculate_discount_pct(original_str, discount_str):
    """
    Hitung persentase diskon dari string harga asli dan harga diskon.
    Mengembalikan string seperti '-33%' atau '' jika tidak ada diskon.
    """
    orig_val = parse_price_value(original_str)
    disc_val = parse_price_value(discount_str)

    if orig_val is None or disc_val is None:
        return ''
    if orig_val == 0:
        return ''
    if orig_val <= disc_val:
        return ''

    pct = round((orig_val - disc_val) / orig_val * 100)
    return f'-{pct}%'


def extract_game_info(game, container_class):
    # --- NAME ---
    name = 'N/A'
    for cls in ['title', 'search_name']:
        elem = game.find('span', {'class': cls})
        if elem:
            name = elem.text.strip()
            break

    # --- PUBLISHED DATE ---
    published_date = 'N/A'
    date_elem = game.find('div', {'class': 'search_released'})
    if date_elem:
        published_date = date_elem.text.strip()

    # --- HARGA ASLI ---
    # Hanya ada jika game sedang diskon; elemen 'discount_original_price' muncul
    original_price_raw = None
    orig_elem = game.find('div', {'class': 'discount_original_price'})
    if orig_elem:
        original_price_raw = orig_elem.text.strip()

    # --- HARGA AKHIR (setelah diskon / harga normal jika tidak diskon) ---
    discount_price_raw = None
    for cls in ['discount_final_price', 'search_price']:
        disc_elem = game.find('div', {'class': cls})
        if disc_elem:
            discount_price_raw = disc_elem.text.strip()
            break

    # Normalisasi: jika tidak ada harga asli terpisah, samakan dengan harga akhir
    # (artinya tidak ada diskon, harga original = harga jual)
    if original_price_raw is None:
        original_price = discount_price_raw if discount_price_raw else 'N/A'
    else:
        original_price = original_price_raw

    discount_price = discount_price_raw if discount_price_raw else 'N/A'

    # --- PERSENTASE DISKON ---
    # Hitung hanya jika memang ada harga asli yang berbeda dari harga akhir
    if original_price_raw is not None:
        discount_pct = calculate_discount_pct(original_price, discount_price)
    else:
        discount_pct = ''  # tidak berdiskon

    # --- REVIEWS ---
    # Tooltip HTML contoh:
    #   "94% of the 128,456 user reviews for this game are positive."
    # Atribut 'data-tooltip-html' berisi label seperti 'Very Positive', 'Mixed', dsb.
    review_summary = game.find('span', {'class': 'search_review_summary'})
    reviews_html = review_summary.get('data-tooltip-html', '') if review_summary else ''

    # Label review diambil langsung dari atribut class pada span
    # Contoh class: 'search_review_summary positive' / 'search_review_summary mixed' dsb.
    # Steam juga menyimpan label teks di dalam tooltip sebelum <br>
    # Format tooltip: "Very Positive<br>94% of the 128,456 user reviews..."
    review_label = 'N/A'
    if review_summary:
        # Coba ambil dari teks tooltip sebelum tag <br>
        label_match = re.match(r'^([^<]+)', reviews_html)
        if label_match:
            review_label = label_match.group(1).strip()

    # Jumlah user yang mereview
    count_match = re.search(r'([\d,]+)\s+user reviews', reviews_html)
    reviews_count = count_match.group(1).replace(',', '') if count_match else 'N/A'

    # Persentase positif
    pct_match = re.search(r'(\d+)%', reviews_html)
    reviews_positive_pct = f"{pct_match.group(1)}%" if pct_match else 'N/A'

    return (
        name,
        published_date,
        original_price,
        discount_price,
        discount_pct,
        reviews_count,
        reviews_positive_pct,
        review_label,
    )


def scrape_filter(filter_name, writer, max_entries=MAX_PER_FILTER, debug=False):
    base_url = f'https://store.steampowered.com/search/?filter={filter_name}'

    response = requests.get(base_url, headers=HEADERS)
    response.raise_for_status()
    doc = BeautifulSoup(response.content, 'html.parser')

    total_pages = get_total_pages(doc)
    print(f"  [{filter_name}] Total pages: {total_pages}")

    line_count = 0

    for page in range(1, total_pages + 1):
        if page == 1:
            page_doc = doc
        else:
            r = requests.get(f"{base_url}&page={page}", headers=HEADERS)
            r.raise_for_status()
            page_doc = BeautifulSoup(r.content, 'html.parser')

        games, container_class = find_game_containers(page_doc)

        if not games:
            print(f"  [{filter_name}] No game containers found on page {page}. "
                  "Run with debug=True to inspect the HTML.")
            break

        print(f"  [{filter_name}] Page {page}: {len(games)} games found")

        for game in games:
            info = extract_game_info(game, container_class)

            # Lewati Steam Deck (hardware, bukan game)
            if info[0].strip().lower() == 'steam deck':
                continue

            writer.writerow([*info, filter_name])
            line_count += 1
            if max_entries and line_count >= max_entries:
                break

        if max_entries and line_count >= max_entries:
            print(f"  [{filter_name}] Reached limit of {max_entries} entries.")
            break

        time.sleep(random.uniform(3, 7))

    print(f"  [{filter_name}] Done — {line_count} entries written.")


def main(search_filters=None, debug=False):
    if search_filters is None:
        search_filters = SEARCH_FILTERS

    output_file = 'games_all.csv'

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Name',
            'Published Date',
            'Original Price',   # Harga sebelum diskon (= Discount Price jika tidak diskon)
            'Discount Price',   # Harga akhir yang dibayar
            'Discount %',       # Persentase diskon (kosong jika tidak ada diskon)
            'Reviews Count',    # Jumlah user yang mereview
            'Reviews Positive', # Persentase review positif
            'Review Label',     # Label review Steam (Very Positive, Mixed, dll.)
            'Search Filter',
        ])

        for filter_name in search_filters:
            print(f"\nScraping filter: {filter_name}")
            scrape_filter(filter_name, writer, debug=debug)

    print(f"\nAll done! Data saved to '{output_file}'.")


if __name__ == '__main__':
    main(
        search_filters=['topsellers', 'mostplayed', 'newreleases', 'upcomingreleases'],
        debug=True,
    )
