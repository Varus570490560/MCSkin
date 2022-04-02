import requests
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


def get_soup():
    pass


def get(url: str, download_mode: bool):
    try:
        response = session.get(url=url, stream=download_mode, headers=headers)
    except Exception as e:
        print(e)
        return None
    return response
