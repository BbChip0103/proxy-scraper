import requests
from bs4 import BeautifulSoup
import threading
import os
import asyncio
import argparse

pathTextFile = ''
proxyType = ''


# From proxyscrape.com 
def proxyscrapeScraper(proxytype, timeout, country):
    response = requests.get("https://api.proxyscrape.com/?request=getproxies&proxytype=" + proxytype + "&timeout=" + timeout + "&country=" + country)
    proxies = response.text
    with open(pathTextFile, "a") as txt_file:
        txt_file.write(proxies)


# From proxy-list.download
def proxyListDownloadScraper(url, type, anon):
    session = requests.session()
    url = url + '?type=' + type + '&anon=' + anon 
    html = session.get(url).text
    if args.verbose:
        print(url)
    with open(pathTextFile, "a") as txt_file:
        for line in html.split('\n'):
            if len(line) > 0:
                txt_file.write(line)


# From sslproxies.org, free-proxy-list.net, us-proxy.org, socks-proxy.net
def makesoup(url):
    page=requests.get(url)
    if args.verbose:
        print(url + ' scraped successfully')
    return BeautifulSoup(page.text,"html.parser")

def proxyscrape(table):
    proxies = set()
    for row in table.findAll('tr'):
        fields = row.findAll('td')
        count = 0
        proxy = ""
        for cell in row.findAll('td'):
            if count == 1:
                proxy += ":" + cell.text.replace('&nbsp;', '')
                proxies.add(proxy)
                break
            proxy += cell.text.replace('&nbsp;', '')
            count += 1
    return proxies

def scrapeproxies(url):
    soup=makesoup(url)
    result = proxyscrape(table = soup.find('table', attrs={'id': 'proxylisttable'}))
    proxies = set()
    proxies.update(result)
    with open(pathTextFile, "a") as txt_file:
        for line in proxies:
	        txt_file.write("".join(line) + "\n")

# From https://proxy-daily.com/
def scrape_proxies_2(url, type_):
    soup=makesoup(url)

    result_list = soup.find_all('div', attrs={'class': 'centeredProxyList'})
    # result_list = [obj for obj in result_list if len(obj.get_text()) < 50 and 'Proxy List:' in obj.get_text()]
    for obj_i, each_obj in enumerate(result_list):
        text = each_obj.get_text()
        if len(text) < 50 and 'Proxy List:' in text:
            if type_ in text.lower():
                result = result_list[obj_i+1].get_text().splitlines()
                break
    proxies = set()
    proxies.update(result)

    with open(pathTextFile, "a") as txt_file:
        for line in proxies:
	        txt_file.write("".join(line) + "\n")


def scrap_main(proxy, pathTextFile):
    if proxy == 'https':
        threading.Thread(target=scrapeproxies, args=('http://sslproxies.org',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'https', 'elite',)).start()
#            threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'https', 'transparent',)).start()
#            threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'https', 'anonymous',)).start()
        # threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'https',)).start()

    if proxy == 'http':
        threading.Thread(target=scrapeproxies, args=('http://free-proxy-list.net',)).start()
        threading.Thread(target=scrapeproxies, args=('http://us-proxy.org',)).start()
        threading.Thread(target=proxyscrapeScraper, args=('http','1000','All',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'http', 'elite',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'http', 'transparent',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'http', 'anonymous',)).start()
        threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'http',)).start()

    if proxy == 'socks':
        threading.Thread(target=scrapeproxies, args=('http://socks-proxy.net',)).start()
        threading.Thread(target=proxyscrapeScraper, args=('socks4','1000','All',)).start()
        threading.Thread(target=proxyscrapeScraper, args=('socks5','1000','All',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'socks4', 'elite',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'socks5', 'elite',)).start()
        threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'socks4',)).start()
        threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'socks5',)).start()

    if proxy == 'socks4':
        threading.Thread(target=proxyscrapeScraper, args=('socks4','1000','All',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'socks4', 'elite',)).start()
        threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'socks4',)).start()

    if proxy == 'socks5':
        threading.Thread(target=proxyscrapeScraper, args=('socks5','1000','All',)).start()
        threading.Thread(target=proxyListDownloadScraper, args=('https://www.proxy-list.download/api/v1/get', 'socks5', 'elite',)).start()
        threading.Thread(target=scrape_proxies_2, args=('https://proxy-daily.com', 'socks5',)).start()

# output watcher
def output(pathTextFile):
    if os.path.exists(pathTextFile):
        os.remove(pathTextFile)
    if not os.path.exists(pathTextFile):
        with open(pathTextFile, 'w'): pass


if __name__ == "__main__":
        global proxy

        parser = argparse.ArgumentParser()
        parser.add_argument("-p", "--proxy", help="Supported proxy type: http ,https, socks, socks4, socks5", required=True)
        parser.add_argument("-o", "--output", help="output file name to save .txt file", default='output.txt')
        parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
        args = parser.parse_args()

        proxy = args.proxy
        pathTextFile = args.output

        if proxy == 'https':
            output(pathTextFile)
            scrap_main(proxy, pathTextFile)
        elif proxy == 'http':
            output(pathTextFile)
            scrap_main(proxy, pathTextFile)
        elif proxy == 'socks':
            output(pathTextFile)
            scrap_main(proxy, pathTextFile)
        elif proxy == 'socks4':
            output(pathTextFile)
            scrap_main(proxy, pathTextFile)
        elif proxy == 'socks5':
            output(pathTextFile)
            scrap_main(proxy, pathTextFile)
        elif proxy == 'all':
            output(pathTextFile)
            scrap_main('https', pathTextFile)
            scrap_main('http', pathTextFile)
            scrap_main('socks', pathTextFile)
            # scrap_main('socks4', pathTextFile)
            # scrap_main('socks5', pathTextFile)
        else:
            assert False
