
import re
import threading

import requests
from bs4 import BeautifulSoup

DOMAIN = "https://django-anuncios.solyd.com.br"
VEHICLES_URL = "https://django-anuncios.solyd.com.br/automoveis/"

LINKS = []
PHONES = []


def request_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print("Erro ao fazer requisição")
    except Exception as error:
        print("Erro ao fazer requisição: {}".format(error))
        

def parsing(html_response):
    try:
        soup = BeautifulSoup(html_response, 'html.parser')
        return soup
    except Exception as error:
        print("Erro ao fazer o parsing HTML: {}".format(error))

def find_links(soup):
    try:
        main_cards = soup.find("div", class_="ui three doubling link cards")
        cards = main_cards.find_all("a")
    except:
        print("Erro ao encontrar links")
        return None

    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except:
            pass

    return links


def find_phones(soup):
    try:
        description = soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
    except:
        print("Erro ai encontrar descricao")
        return None

    regex_phones = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", description)
    if regex_phones:
        return regex_phones


def discover_phones():
    while True:
        try:
            ad_link = LINKS.pop(0)
        except:
            return None
        ad_response = request_url(DOMAIN + ad_link)
        if ad_response:
            soup_ad = parsing(ad_response)
            if soup_ad:
                phones = find_phones(soup_ad)
                if phones:
                    for phone in phones:
                        print("phone encontrado:", phone)
                        PHONES.append(phone)
                        save_phone(phone)


def save_phone(phone):
    string_phone = "({}) {}-{}\n".format(phone[0], phone[1], phone[2])
    try:
        with open("phones.csv", "a") as file:
            file.write(string_phone)
    except Exception as error:
        print("Erro ao salvar arquivo")
        print(error)


if __name__ == "__main__":
    request_response = request_url(VEHICLES_URL)
    if request_response:
        request_soup = parsing(request_response)
        if request_soup:
            LINKS = find_links(request_soup)

            THREADS = []
            for i in range(10):
                t = threading.Thread(target=discover_phones)
                THREADS.append(t)

            for t in THREADS:
                t.start()

            for t in THREADS:
                t.join()
