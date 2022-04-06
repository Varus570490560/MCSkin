from bs4 import BeautifulSoup
import minecraft_skin_lib

import http_request


def crawl_minecraftskinstealer():
    base_url = 'https://minecraft-statistic.net/en/skins/'
    skin_count = 90
    while True:
        print(f"Page = {skin_count}")
        response = http_request.get(url=base_url + str(skin_count))
        if response.status_code == 404:
            break
        soup = BeautifulSoup(response.content, 'lxml')
        skins = soup.findAll(name='div', attrs='col-md-4 col-sm-4 col-xs-6')
        for skin in skins:
            url = skin.div.a['href']
            name = skin.div.div.strong.text

            response = http_request.get(url=url)
            soup = BeautifulSoup(response.content, 'lxml')
            download_url = soup.find(name='a', attrs='btn btn-lg btn-primary btn-block m-b-25')['href']
            minecraft_skin_lib.this.submit_skin(source_skin_image_url=download_url, data_source='minecraftskinstealer',
                                                name=name)
            print(f"Download_url = {download_url} \nname = {name}")
        skin_count = skin_count + 30


if __name__ == '__main__':
    crawl_minecraftskinstealer()
