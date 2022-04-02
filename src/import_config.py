import configparser


class CrawlConfig:
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read('./config/crawl_config.ini')
        self.mysql_host = cf.get('mysql', 'host')
        self.mysql_user = cf.get('mysql', 'user')
        self.mysql_password = cf.get('mysql', 'password')
        self.mysql_port = cf.get('mysql', 'port')