import requests
from bs4 import BeautifulSoup

def scan_website(url):
    url=url.strip()
    response = requests.get(
        url,
        headers={"User-Agent": "Reverse-OSINT-Analyzer"},
        timeout=10
    )

    soup = BeautifulSoup(response.text, "html.parser")

    scripts = []
    for script in soup.find_all("script"):
        scripts.append(script.get_text())

    return scripts
