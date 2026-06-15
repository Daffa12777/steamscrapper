import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random
import os
import json


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

SEARCH_FILTERS = ['topsellers', 'mostplayed', 'newreleases', 'upcomingreleases']
MAX_PER_FILTER = 1000
MAX_PAGES_PER_CATEGORY = 100

CACHE_FILE = 'category_maps_cache.json'

CATEGORY_GROUPS = {
    'Number Of Players': [
        ('Singleplayer',               'https://store.steampowered.com/search?category3=2&ndl=1'),
        ('Multi-player',                'https://store.steampowered.com/search?category3=1&ndl=1'),
        ('PvP',                          'https://store.steampowered.com/search?category3=49&ndl=1'),
        ('Online PvP',                   'https://store.steampowered.com/search?category3=36&ndl=1'),
        ('LAN PvP',                      'https://store.steampowered.com/search?category3=47&ndl=1'),
        ('Shared/Split Screen PvP',      'https://store.steampowered.com/search?category3=37&ndl=1'),
        ('Co-op',                        'https://store.steampowered.com/search?category3=9&ndl=1'),
        ('Online Co-op',                 'https://store.steampowered.com/search?category3=38&ndl=1'),
        ('LAN Co-op',                    'https://store.steampowered.com/search?category3=48&ndl=1'),
        ('Shared/Split Screen Co-op',    'https://store.steampowered.com/search?category3=39&ndl=1'),
        ('Shared/Split Screen',          'https://store.steampowered.com/search?category3=24&ndl=1'),
        ('Cross-Platform Multiplayer',   'https://store.steampowered.com/search?category3=27&ndl=1'),
    ],
    'Controller Support': [
        ('Gamepad Preferred',            'https://store.steampowered.com/search?controllersupport=60&ndl=1'),
        ('Full Controller Support',      'https://store.steampowered.com/search?controllersupport=28&ndl=1'),
        ('Xbox Controller Support',      'https://store.steampowered.com/search?controllersupport=18&ndl=1'),
        ('DualShock Controller Support', 'https://store.steampowered.com/search?controllersupport=55&ndl=1'),
        ('Dualsense Controller Support', 'https://store.steampowered.com/search?controllersupport=57&ndl=1'),
        ('Steam Input API Support',      'https://store.steampowered.com/search?controllersupport=59&ndl=1'),
    ],
    'OS': [
        ('Windows',         'https://store.steampowered.com/search?os=win&ndl=1'),
        ('macOS',           'https://store.steampowered.com/search?os=mac&ndl=1'),
        ('SteamOS + Linux', 'https://store.steampowered.com/search?os=linux&ndl=1'),
    ],
}


def get_total_pages(doc):
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


def get_name(game):
    for cls in ['title', 'search_name']:
        elem = game.find('span', {'class': cls})
        if elem:
            return elem.text.strip()
    return 'N/A'


def get_appid(game, container_class):
    if container_class == 'search_result_row':
        container = game
    else:
        container = game.find_parent('a', {'class': 'search_result_row'})

    if not container:
        return None

    raw = container.get('data-ds-appid')
    if not raw:
        return None

    return raw.split(',')[0].strip()


def parse_price_value(price_str):
    if not price_str or price_str in ('N/A', 'Free', 'Free To Play'):
        return None
    cleaned = re.sub(r'[^\d.,]', '', price_str).replace(',', '.')
    match = re.search(r'\d+(?:\.\d+)?', cleaned)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def calculate_discount_pct(original_str, discount_str):
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
    appid = get_appid(game, container_class)
    name = get_name(game)

    published_date = 'N/A'
    date_elem = game.find('div', {'class': 'search_released'})
    if date_elem:
        published_date = date_elem.text.strip()

    original_price_raw = None
    orig_elem = game.find('div', {'class': 'discount_original_price'})
    if orig_elem:
        original_price_raw = orig_elem.text.strip()

    discount_price_raw = None
    for cls in ['discount_final_price', 'search_price']:
        disc_elem = game.find('div', {'class': cls})
        if disc_elem:
            discount_price_raw = disc_elem.text.strip()
            break

    original_price = original_price_raw if original_price_raw else (discount_price_raw or 'N/A')
    discount_price = discount_price_raw or 'N/A'
    discount_pct   = calculate_discount_pct(original_price, discount_price) if original_price_raw else 'N/A'

    review_summary = game.find('span', {'class': 'search_review_summary'})
    reviews_html   = review_summary.get('data-tooltip-html', '') if review_summary else ''

    review_label = 'N/A'
    if review_summary:
        label_match = re.match(r'^([^<]+)', reviews_html)
        if label_match:
            review_label = label_match.group(1).strip()

    count_match        = re.search(r'([\d,]+)\s+user reviews', reviews_html)
    reviews_count      = count_match.group(1).replace(',', '') if count_match else 'N/A'

    pct_match          = re.search(r'(\d+)%', reviews_html)
    reviews_positive   = f"{pct_match.group(1)}%" if pct_match else 'N/A'

    return (
        appid,
        name,
        published_date,
        original_price,
        discount_price,
        discount_pct,
        reviews_count,
        reviews_positive,
        review_label,
    )



def scrape_category_appids(url, label, max_pages=None):
    appids = set()

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    doc = BeautifulSoup(response.content, 'html.parser')

    total_pages = get_total_pages(doc)
    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"    [{label}] total halaman akan di-crawl: {total_pages}")

    for page in range(1, total_pages + 1):
        if page == 1:
            page_doc = doc
        else:
            sep = '&' if '?' in url else '?'
            r = requests.get(f"{url}{sep}page={page}", headers=HEADERS)
            r.raise_for_status()
            page_doc = BeautifulSoup(r.content, 'html.parser')

        games, container_class = find_game_containers(page_doc)
        if not games:
            break

        for game in games:
            if get_name(game).strip().lower() == 'steam deck':
                continue
            appid = get_appid(game, container_class)
            if appid:
                appids.add(appid)

        print(f"    [{label}] halaman {page}: {len(games)} game, total unik {len(appids)}")
        time.sleep(random.uniform(2, 4))

    return appids


def build_category_maps(groups=CATEGORY_GROUPS, max_pages=MAX_PAGES_PER_CATEGORY,
                         use_cache=True, cache_file=CACHE_FILE):
    if use_cache and os.path.exists(cache_file):
        print(f"Memuat peta kategori dari cache: {cache_file}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return {
            group: {appid: set(labels) for appid, labels in members.items()}
            for group, members in raw.items()
        }

    maps = {}
    for group_name, entries in groups.items():
        print(f"\n=== Membangun peta kategori: {group_name} ===")
        membership = {}
        for label, url in entries:
            print(f"  Scraping label: {label}")
            appids = scrape_category_appids(url, label, max_pages=max_pages)
            for appid in appids:
                membership.setdefault(appid, set()).add(label)
            print(f"  [{label}] -> {len(appids)} appid ditemukan")
        maps[group_name] = membership

    if use_cache:
        serializable = {
            group: {appid: sorted(labels) for appid, labels in members.items()}
            for group, members in maps.items()
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
        print(f"\nPeta kategori disimpan ke cache: {cache_file}")

    return maps


def lookup_categories(category_maps, group_name, appid):
    if not appid:
        return 'N/A'
    labels = category_maps.get(group_name, {}).get(appid)
    if not labels:
        return 'N/A'
    return ', '.join(sorted(labels))

def scrape_filter(filter_name, category_maps, max_entries=MAX_PER_FILTER):
    base_url = f'https://store.steampowered.com/search/?filter={filter_name}'

    response = requests.get(base_url, headers=HEADERS)
    response.raise_for_status()
    doc = BeautifulSoup(response.content, 'html.parser')

    total_pages = get_total_pages(doc)
    print(f"  [{filter_name}] Total halaman: {total_pages}")

    rows = []
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
            print(f"  [{filter_name}] Tidak ada game pada halaman {page}.")
            break

        print(f"  [{filter_name}] halaman {page}: {len(games)} game ditemukan.")

        for game in games:
            info = extract_game_info(game, container_class)
            appid, name = info[0], info[1]

            if name.strip().lower() == 'steam deck':
                continue

            num_players = lookup_categories(category_maps, 'Number Of Players', appid)
            controller  = lookup_categories(category_maps, 'Controller Support', appid)
            os_support  = lookup_categories(category_maps, 'OS', appid)
            rows.append([*info, filter_name, num_players, controller, os_support])
            line_count += 1
            if max_entries and line_count >= max_entries:
                break

        if max_entries and line_count >= max_entries:
            print(f"  [{filter_name}] limit telah dicapai {max_entries} masukan.")
            break

        time.sleep(random.uniform(3, 7))

    print(f"  [{filter_name}] Selesai — {line_count} masukan ditemukan.")
    return rows


def dedupe_rows(all_rows):
    SEARCH_FILTER_COL = 9  

    deduped = {}
    order = []

    for row in all_rows:
        appid = row[0]
        key = ('appid', appid) if appid else ('name', row[1].strip().lower())

        if key not in deduped:
            deduped[key] = list(row)
            order.append(key)
            continue

        existing = deduped[key]
        existing_filters = {
            v.strip() for v in existing[SEARCH_FILTER_COL].split(',')
            if v.strip() and v.strip() != 'N/A'
        }
        new_filter = row[SEARCH_FILTER_COL]
        if new_filter and new_filter != 'N/A':
            existing_filters.add(new_filter)

        existing[SEARCH_FILTER_COL] = ', '.join(sorted(existing_filters)) if existing_filters else 'N/A'

    return [deduped[key] for key in order]


def main(search_filters=None, max_pages_per_category=MAX_PAGES_PER_CATEGORY, use_cache=True):
    if search_filters is None:
        search_filters = SEARCH_FILTERS

    output_file = 'games_all.csv'

    print("=== Tahap 1: Membangun peta kategori (Number Of Players / Controller Support / OS) ===")
    category_maps = build_category_maps(max_pages=max_pages_per_category, use_cache=use_cache)

    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'AppID',
            'Name',
            'Published Date',
            'Original Price',
            'Discount Price',
            'Discount %',
            'Reviews Count',
            'Reviews Positive',
            'Review Label',
            'Search Filter',        
            'Number Of Players',       
            'Controller Support',      
            'OS',                      
        ])

        print("\n=== Tahap 2: Scraping daftar game utama ===")
        all_rows = []
        for filter_name in search_filters:
            print(f"\nScraping filter: {filter_name}")
            all_rows.extend(scrape_filter(filter_name, category_maps))

        print(f"\nTotal sebelum dedup: {len(all_rows)} baris.")
        deduped_rows = dedupe_rows(all_rows)
        print(f"Total setelah dedup: {len(deduped_rows)} baris.")

        for row in deduped_rows:
            writer.writerow(row)

    print(f"\nData disimpan ke file '{output_file}'.")


if __name__ == '__main__':
    main(
        search_filters=['topsellers', 'mostplayed', 'newreleases', 'upcomingreleases'],
        max_pages_per_category=100,
        use_cache=True,
    )
