import configparser


class CrawlConfig:

    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read('../config/crawl_config.ini')
        self.mysql_host = cf.get('mysql', 'host')
        self.mysql_user = cf.get('mysql', 'user')
        self.mysql_password = cf.get('mysql', 'password')
        self.mysql_port = cf.get('mysql', 'port')
        self.project_path = cf.get('path', 'project_path')
        self.skin_download_path = cf.get('path', 'skin_download_path')
        self.sql_export_path = cf.get('path', 'sql_export_path')


config: CrawlConfig = CrawlConfig()
