import bs4.element
from bs4 import BeautifulSoup
import minecraft_skin_lib

import http_requests


def crawl_minecraftskinstealer():
    base_url = 'https://minecraft-statistic.net/en/skins/'
    skin_count = 0
    while True:
        print(f"Page = {skin_count}")
        response = http_requests.get(url=base_url + str(skin_count))
        if response.status_code == 404:
            break
        soup = BeautifulSoup(response.content, 'lxml')
        skins = soup.findAll(name='div', attrs='col-md-4 col-sm-4 col-xs-6')
        for skin in skins:
            url = skin.div.a['href']
            name = skin.div.div.strong.text

            response = http_requests.get(url=url)
            soup = BeautifulSoup(response.content, 'lxml')
            download_url = soup.find(name='a', attrs='btn btn-lg btn-primary btn-block m-b-25')['href']
            minecraft_skin_lib.this.submit_skin(source_skin_image_url=download_url, data_source='minecraftskinstealer',
                                                name=name)
            print(f"Download_url = {download_url} \nname = {name}")
        skin_count = skin_count + 30


def crawl_plant_mc():
    pass


def crawl_mcskin_top():
    base_url = 'https://mcskins.top'
    skin_page = 1
    while True:
        print(f'Page :{skin_page}')
        if skin_page == 241:
            break
        soup: bs4.element.Tag = http_requests.get_soup(url=base_url + '/page/' + str(skin_page)).soup
        skins = soup.findAll(name='a', attrs='title-link')
        for skin in skins:
            soup = http_requests.get_soup(url=base_url + skin['href']).soup
            skin_name = soup.find(name='div', attrs='section download').div.b.text[9:]
            skin_image_url = base_url + soup.find(name='div', attrs='section download').a['href']
            minecraft_skin_lib.this.submit_skin(source_skin_image_url=skin_image_url, data_source='MCskin_top', name=skin_name)
            print(f"name: {skin_name} url:{skin_image_url}")
        skin_page = skin_page + 1


def crawl_needcoolshoes():
    base_url: str = 'https://www.needcoolshoes.com/gallery?page='
    skin_page = 1
    while True:
        print(f'Page :{skin_page}')
        soup = http_requests.get_soup(url=base_url + str(skin_page)).soup
        skins = soup.findAll(name='div', attrs='skin-item')
        if len(skins) == 0:
            break
        for skin in skins:
            url = skin.div.a['href']
            soup = http_requests.get_soup(url=url).soup
            skin_image_url = soup.find(name='div', attrs='model checker-border')['data-save']
            skin_name = soup.find(name='h1', attrs={'itemprop': 'name'}).text
            skin_author = soup.find(name='a', attrs={'itemprop': 'author'}).text
            print(skin_name, skin_author, skin_image_url)
            minecraft_skin_lib.this.submit_skin(source_skin_image_url=skin_image_url, data_source='needcoolshoes', author=skin_author, name=skin_name)
        skin_page += 1


if __name__ == '__main__':
    crawl_needcoolshoes()
