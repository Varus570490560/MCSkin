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


def get_soup(url: str, features: str='html.parser'):
    response = session.get(url=url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Http response status code {response.status_code}.")
    soup = BeautifulSoup(response.content, features=features)
    return soup


def get(url: str, download_mode: bool = False):
    try:
        response = session.get(url=url, stream=download_mode, headers=headers, timeout=30)
    except Exception as e:
        print(e)
        return None
    return response
