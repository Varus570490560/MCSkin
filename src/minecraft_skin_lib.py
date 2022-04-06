import hashlib
import hmac
import os
import random

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

    def export(self, skin_count: int):
        skins_lst = list(connect_database.execute_sql(db=self.db,
                                                      sql="SELECT * FROM `skin_lib` WHERE `id` IN (SELECT min(`id`) FROM `skin` GROUP BY `sha256`)  AND `size` = '(64, 64)' AND `in_use` = 0"))
        random.shuffle(skins_lst)
        res = skins_lst[0:skin_count]
        sha256_lst: list = list()
        for data in res:
            sha256_lst.append(data[10])
        with open("../sql/export.sql", 'wb') as writer:
            writer.write(
                "INSERT INTO `mc_skin_reserve` (`name`, `author`, `skin_image_url`, `description`, `preview_image_url`) VALUES \n".encode())
            i: int = 0
            for skin in res:
                author = skin[2]
                if author is None:
                    author = 'Anonymous'
                else:
                    author = MinecraftSkinLib.__transferred_meaning(skin[2])
                skin_name = MinecraftSkinLib.__transferred_meaning(skin[1])
                skin_image_url = MinecraftSkinLib.__transferred_meaning(skin[3])
                description = MinecraftSkinLib.__transferred_meaning(skin[6])
                writer.write(f"        ('{skin_name}', '{author}', '{skin_image_url}', '{description}','')".encode())
                if i < skin_count - 1:
                    writer.write(',\n'.encode())
                i = i + 1
            writer.write(';'.encode())
        for sha256 in sha256_lst:
            connect_database.execute_sql(db=self.db, sql="UPDATE `skin_lib` SET `in_use` = 1 WHERE `sha256` = %s;",
                                         args=(sha256,))

    @staticmethod
    def __transferred_meaning(words: str):
        if words is None:
            return ""
        return words.replace("'", "\\'")

    def submit_skin(self, source_skin_image_url: str, data_source: str, name: str = '', author: str = '',
                    description: str = '', model: str = ''):
        skin_id = self.__download_skin(source_skin_image_url=source_skin_image_url)
        size: str = MinecraftSkinLib.__get_size(skin_id=skin_id)
        sha256 = MinecraftSkinLib.__get_sha256(skin_id=skin_id)
        in_use: int = 0
        if connect_database.execute_sql(db=self.db, sql="SELECT count(1) FROM `skin_lib` WHERE sha256 = %s AND in_use = 1",
                                        args=(sha256,))[0][0] >= 1:
            in_use = 1
        if model == '' and size == '(64, 64)':
            model = MinecraftSkinLib.__get_model(skin_id=skin_id)
        if skin_id == 0:
            return False
        skin_information = {
            'name': name,
            'author': author,
            'skin_image_url': MinecraftSkinLib.__get_skin_image_url(skin_id=skin_id),
            'source_skin_image_url': source_skin_image_url,
            'description': description,
            'data_source': data_source,
            'in_use': in_use,
            'size': size,
            'model': model,
            'sha256': sha256,
            'passageway': MinecraftSkinLib.__get_passageway(skin_id=skin_id),
        }
        return connect_database.save(db=self.db, table_name='skin_lib', val=skin_information,
                                     unique_keys=("source_skin_image_url",))

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

    @staticmethod
    def __get_passageway(skin_id: int):
        picture_file_name = MinecraftSkinLib.__get_picture_name_by_id(skin_id=skin_id)
        with Image.open(picture_file_name) as image:
            bands = image.getbands()
            passageway = ''
            for band in bands:
                passageway = passageway + band
        return passageway

    @staticmethod
    def __get_size(skin_id: int):
        picture_file_name = MinecraftSkinLib.__get_picture_name_by_id(skin_id=skin_id)
        with Image.open(picture_file_name) as image:
            size: str = str(image.size)
        return size

    @staticmethod
    def __get_sha256(skin_id: int):
        picture_file_name = MinecraftSkinLib.__get_picture_name_by_id(skin_id=skin_id)
        skin_fingerprint = list()
        with Image.open(picture_file_name) as image:
            image_array: Image = image.load()
            for i in range(0, image.size[0]):
                for j in range(0, image.size[1]):
                    skin_fingerprint.append(image_array[i, j])
        skin_fingerprint = str(skin_fingerprint).encode("utf-8")
        return hmac.new(skin_fingerprint, digestmod=hashlib.md5).hexdigest().upper()

    @staticmethod
    def __get_skin_image_url(skin_id: int):
        base_url = 'https://cdn.ezjojoy.com/mcskins'
        grandparent_dir = str(skin_id // 100 % 100)
        parent_dir = str(skin_id % 100)
        if len(parent_dir) == 1:
            parent_dir = '0' + parent_dir
        if len(grandparent_dir) == 1:
            grandparent_dir = '0' + grandparent_dir
        return base_url + '/' + grandparent_dir + '/' + parent_dir + '/' + str(skin_id) + '.png'

    @staticmethod
    def __get_model(skin_id: int):
        check_points = (
            (46, 52), (47, 52), (46, 53), (47, 53), (46, 54), (47, 54), (46, 55), (47, 55), (46, 56), (47, 56),
            (46, 57), (47, 57), (46, 58), (47, 58), (46, 59), (47, 59), (46, 60), (47, 60), (46, 61), (47, 61),
            (46, 62), (47, 62), (46, 63), (47, 63), (62, 52), (63, 52), (62, 53), (63, 53), (62, 54), (63, 54),
            (62, 55), (63, 55), (62, 56), (63, 56), (62, 57), (63, 57), (62, 58), (63, 58), (62, 59), (63, 59),
            (62, 60), (63, 60), (62, 61), (63, 61), (62, 62), (63, 62), (62, 63), (63, 63))
        picture_file_name = MinecraftSkinLib.__get_picture_name_by_id(skin_id=skin_id)
        with Image.open(picture_file_name) as image:
            if MinecraftSkinLib.__get_passageway(skin_id=skin_id) != 'RGBA':
                return ''
            for point in check_points:
                if image.getpixel(point)[3] ==255:
                    return 'steve'
            return 'alex'

    # This function for test, Please don't call this function.
    def __save_test(self, id: int, name: str, author: str, skin_image_url: str, description: str, data_source: str,
                    in_use: int, size: str, model: str, sha256: str, passageway: str):
        skin_information = {
            'name': name,
            'author': author,
            'skin_image_url': skin_image_url,
            'source_skin_image_url': '',
            'description': description,
            'data_source': data_source,
            'in_use': in_use,
            'size': size,
            'model': model,
            'sha256': sha256,
            'passageway': passageway,
        }
        return connect_database.save(db=self.db, table_name='skin_lib', val=skin_information)

    # This function for test, Please don't call this function.
    def __set_in_use(self):
        skins = connect_database.execute_sql(db=self.db, sql="SELECT * FROM `mc_skin`;")
        sha256_lst: list = list()
        for skin in skins:
            sha256 = connect_database.execute_sql(db=self.db,
                                                  sql="SELECT sha256 FROM `skin` WHERE `skin_image_url` = %s",
                                                  args=(skin[3],))
            sha256_lst.append(sha256[0][0])
        for sha256 in sha256_lst:
            connect_database.execute_sql(db=self.db, sql="UPDATE `skin_lib` SET `in_use` = 1 WHERE `sha256` = %s;",
                                         args=(sha256,))


this: MinecraftSkinLib = MinecraftSkinLib()
