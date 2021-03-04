import requests
import tqdm
import json
import datetime
from http.client import responses

token_vk = ''
token_ya = ''


class VK:
    API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, token: str, user_id, version='5.130'):
        self.types = {'s': 1, 'm': 2, 'x': 3, 'o': 4, 'p': 5, 'q': 6, 'r': 7, 'y': 8, 'z': 9, 'w': 10}
        self.vk_site = 'https://vk.com/'
        self.token = token
        self.version = version
        self.user_id = user_id
        response = requests.get(self.API_BASE_URL + 'photos.get',
                                params={'owner_id': self.user_id, 'photo_sizes': 1, 'count': 5, 'album_id': 'profile',
                                        'extended': 1, 'access_token': token, 'v': 5.130})

        photos = response.json()
        self.photos = photos['response']['items']

    def get_photo(self):
        result = []
        download_files = []
        print('загрузка фотографий:')
        for item in tqdm.tqdm(self.photos):
            max_size = 0
            download_link = {}
            for link in item['sizes']:
                if max_size > self.types.get(link['type']):
                    continue
                else:
                    max_size = self.types.get(link['type'])
                    download_link = link
            url1 = download_link['url']
            date = datetime.datetime.fromtimestamp(item['date'])
            name = str(date.strftime('%d-%m-%y')) + 'id' + str(item['id']) + '.jpg'
            result.append(name)
            download_files.append({'file_name': name, 'size': download_link['type']})
            response = requests.get(url1)
            with open(name, 'wb') as f:
                f.write(response.content)

        with open("data_file.json", "w") as write_file:
            json.dump(download_files, write_file)
        return result


class Yandex:
    def __init__(self, token: str):
        self.TOKEN = {'Authorization': 'OAuth' + token}
        self.HOST_API = 'https://cloud-api.yandex.net:443'
        self.UPLOAD_LINK = '/v1/disk/resources/upload'
        self.FILES_LIST = '/v1/disk/resources/files'
        self.FOLDER_CREATE = '/v1/disk/resources'
        self.FILES = files

    def upload(self):
        print('Загрузка файлов на Яндекс Диск')
        folder_u = self.create_folder()
        for item in tqdm.tqdm(self.FILES):
            path = folder_u + '/' + item
            upload_link = requests.get(self.HOST_API + self.UPLOAD_LINK, params={'path': path}, headers=self.TOKEN)
            if upload_link.status_code != requests.codes.ok:
                return f'\nОшибка при получении URL. Код: ' \
                       f'{upload_link.status_code} ({responses[upload_link.status_code]})'
            files_1 = {'file': open(item, 'rb')}
            request = requests.put(upload_link.json()['href'], params={'path': item}, files=files_1)
            if not (200 <= request.status_code < 300):
                return print(f'\nОшибка при загрузке файла. Код: '
                             f'{request.status_code} ({responses[request.status_code]})')
        return print(f'\nФайлы загружены. Код: {request.status_code} ({responses[request.status_code]})')

    def create_folder(self, folder_name='test'):
        folder_1 = requests.put(self.HOST_API + self.FOLDER_CREATE,
                                params={'path': folder_name}, headers=self.TOKEN)
        if not (200 <= folder_1.status_code < 300):
            return f'\nОшибка при при создании папки. Код: ' \
                   f'{folder_1.status_code} ({responses[folder_1.status_code]})'
        return folder_name

    def file_list(self):
        result = []
        request = requests.get(self.HOST_API + self.FILES_LIST, headers=self.TOKEN)
        if not (200 <= request.status_code < 300):
            return [f'\nОшибка при получении списка файлов. Код: '
                    f'{request.status_code} ({responses[request.status_code]})']
        result += [f'({x["name"]} ({str(int(x["size"] / 1024))} kB )' for x in request.json()['items']]
        return print(result)


user_1 = VK(token_vk, '')
folder = 'test'
files = user_1.get_photo()
uploader = Yandex(token_ya)
uploader.upload()
uploader.file_list()
