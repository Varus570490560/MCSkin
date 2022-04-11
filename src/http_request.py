import time

import bs4.element
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3 import Retry

user_agent = UserAgent()
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter=adapter)
session.mount('https://', adapter=adapter)
headers = {
    'User-Agent': user_agent.random
}


class Response:
    status_code: int
    soup: bs4.element.Tag

    def __init__(self, status_code: int, soup: bs4.element.Tag):
        self.soup = soup
        self.status_code = status_code


def get_soup(url: str, features: str = 'html.parser'):
    try:
        response = session.get(url=url, headers=headers, timeout=30)
    except Exception as e:
        print(e)
        print("There is a exception occurred. Let me have a rest.")
        time.sleep(120)
        return get_soup(url=url, features=features)
    soup = BeautifulSoup(response.content, features=features)
    return Response(status_code=response.status_code, soup=soup)


def get(url: str, download_mode: bool = False):
    try:
        response = session.get(url=url, stream=download_mode, headers=headers, timeout=30)
    except Exception as e:
        print(e)
        print("There is a exception occurred. Let me have a rest.")
        time.sleep(120)
        return get(url=url, download_mode=download_mode)
    return response
