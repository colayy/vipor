import requests
from bs4 import BeautifulSoup
import time
from geopy.geocoders import Nominatim
from requests.exceptions import RequestException

# URL situs penyedia proxy
proxy_url = "https://www.freeproxylists.net/"

# Fungsi untuk mendapatkan daftar proxy
def get_proxy_list(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Gagal mengakses situs proxy")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'DataGrid'})
    proxies = []

    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) > 0:
                ip = cols[0].get_text(strip=True)
                port = cols[1].get_text(strip=True)
                country = cols[3].get_text(strip=True)
                type_ = cols[4].get_text(strip=True)
                proxy = {
                    "ip": ip,
                    "port": port,
                    "country": country,
                    "type": type_
                }
                proxies.append(proxy)
    
    return proxies

# Fungsi untuk memeriksa apakah proxy aktif dan mengukur kecepatan
def check_proxy_speed(proxy, timeout=5):
    url = "https://httpbin.org/ip"  # URL untuk diuji
    proxies = {
        "http": f"http://{proxy['ip']}:{proxy['port']}",
        "https": f"https://{proxy['ip']}:{proxy['port']}"
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            return True, elapsed_time
        else:
            return False, None
    except RequestException:
        return False, None

# Fungsi untuk menyaring proxy berdasarkan tipe dan negara
def filter_proxies(proxies, types=None, countries=None):
    filtered_proxies = []
    for proxy in proxies:
        if types and proxy['type'].lower() not in types:
            continue
        if countries and proxy['country'].lower() not in countries:
            continue
        filtered_proxies.append(proxy)
    return filtered_proxies

# Fungsi untuk menyimpan proxy ke file
def save_proxies_to_file(proxies, filename="proxies.txt"):
    with open(filename, "w") as f:
        for proxy in proxies:
            f.write(f"{proxy['ip']}:{proxy['port']} - {proxy['type']} - {proxy['country']}\n")
    print(f"Daftar proxy disimpan ke {filename}")

def main():
    # Mengambil daftar proxy dari situs
    print("Mengambil daftar proxy...")
    proxies = get_proxy_list(proxy_url)
    print(f"Ditemukan {len(proxies)} proxy.")

    # Filter proxy berdasarkan tipe (HTTP/HTTPS/SOCKS) dan negara (misalnya "US")
    filter_types = ["http", "https"]  # Jenis proxy yang diinginkan
    filter_countries = ["us"]  # Negara yang diinginkan, bisa sesuaikan

    print(f"Menyaring proxy berdasarkan tipe: {filter_types} dan negara: {filter_countries}...")
    filtered_proxies = filter_proxies(proxies, types=filter_types, countries=filter_countries)
    print(f"Proxy setelah disaring: {len(filtered_proxies)}")

    # Mengecek kecepatan dan validitas proxy
    valid_proxies = []
    for proxy in filtered_proxies:
        print(f"Menguji proxy {proxy['ip']}:{proxy['port']}...")
        is_valid, speed = check_proxy_speed(proxy)
        if is_valid:
            print(f"Proxy {proxy['ip']}:{proxy['port']} valid dengan waktu respon {speed:.2f} detik")
            valid_proxies.append(proxy)
        else:
            print(f"Proxy {proxy['ip']}:{proxy['port']} tidak valid")

    # Simpan proxy yang valid ke file
    save_proxies_to_file(valid_proxies)

if __name__ == "__main__":
    main()
