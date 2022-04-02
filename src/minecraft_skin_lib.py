import os

import pymysql
from PIL import Image

import connect_database
import import_config
import http_request


class MinecraftSkinLib:
    db: pymysql.connections.Connection

    def __init__(self):
        try:
            self.db = connect_database.open_database(database_name='mc_skin')
        except pymysql.Error as e:
            print(e)

    def __del__(self):
        connect_database.close_database(db=self.db)

    def export(self):
        pass

    def submit_skin(self, source_skin_image_url: str, data_source: str, name: str = '', author: str = '',
                    description: str = ''):
        skin_id = self.__download_skin(source_skin_image_url=source_skin_image_url)
        if skin_id == 0:
            return False

        pass

    @staticmethod
    def __is_valid(file):
        valid = True
        try:
            Image.open(fp=file).load()
        except OSError:
            valid = False
        return valid

    @staticmethod
    def __get_picture_name_by_id(skin_id: int):
        return MinecraftSkinLib.__get_picture_dir_by_id(skin_id=skin_id) + '/' + str(skin_id) + '.png'

    @staticmethod
    def __get_picture_dir_by_id(skin_id: int):
        skin_download_path = import_config.config.skin_download_path
        grandparent_dir: str = str(skin_id % 100)
        if len(grandparent_dir) == 1:
            grandparent_dir = '0' + grandparent_dir
        parent_dir: str = str(skin_id // 100 % 100)
        if len(parent_dir) == 1:
            parent_dir = '0' + parent_dir
        return skin_download_path + grandparent_dir + '/' + parent_dir

    def __download_skin(self, source_skin_image_url: str):
        auto_increment: int = connect_database.execute_sql(self.db,
                                                           'SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = "skin_lib"')[
            0][0]
        skin_dir = self.__get_picture_dir_by_id(auto_increment)
        skin_file_name = self.__get_picture_name_by_id(auto_increment)
        if not os.path.exists(skin_dir):
            os.makedirs(skin_dir)
        response = http_request.get(url=source_skin_image_url, download_mode=True)
        if response.status_code != 200:
            print(f'Download fail! Get url = {source_skin_image_url} response status code = {response.status_code}.')
            return 0
        with open(file=skin_file_name, mode='wb') as writer:
            writer.write(response.content)
        if self.__is_valid(skin_file_name):
            return auto_increment
        else:
            print(f'Picture format verification failed! url = {source_skin_image_url}')
            return 0
