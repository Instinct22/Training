import requests
from requests import HTTPError
import json
import os

class yc_env:
    def __init__(self):
        self.iam_token = self.iam_token_create()
        self.data = {
            "iam_token": f"{self.iam_token}"
        }
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}"
        }

    # Создаем IAM токен
    def iam_token_create(self):
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        data = {
            "yandexPassportOauthToken": os.getenv("OAuth")
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()
            if response.status_code == 200:
                iam_token = response_data.get("iamToken")

                return iam_token

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Отзываем IAM токен
    def revoke_token(self):
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens:revoke"

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(self.data))
            response_data = response.json()

            if response.status_code == 200:
                print("IAM token отозван")

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Достаем id нашего облака (Кривое условие, рассчитано под мою задачу, с 1 облаком)
    def cloud_list(self):
        url = "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/clouds"
        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                cloud_id = response_data['clouds'][0]['id']
                return cloud_id

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Получение списка папок (Кривое условие, рассчитано под мою задачу, с 1 папкой). Проверить корректность папки можно через консоль перейдя в папку и посмотреть на URL
    def folder_list(self):
        url = "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders"
        params = {
            "cloudId": f"{self.cloud_list()}"
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response_data = response.json()

            if response.status_code == 200:
                folders_id = response_data['folders'][0]['id']
                return folders_id

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Получаем наименование подсети (в моем случае не важно какая)
    def zone_list(self):
        url = "https://compute.api.cloud.yandex.net/compute/v1/zones"
        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                zones_id = response_data['zones'][0]['id']
                return zones_id

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Получаем типа диска
    def disk_type_list(self):
        url = "https://compute.api.cloud.yandex.net/compute/v1/diskTypes"
        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                diskTypes = response_data['diskTypes'][0]['id']

                return diskTypes

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Получаем список image. Использовал standard-images.
    def image_list(self):
        url = "https://compute.api.cloud.yandex.net/compute/v1/images"
        params = {
            "folderId": "standard-images",
            "filter": "name='ubuntu-24-04-lts-v20250106'",
            "pageSize": "100"
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response_data = response.json()

            if response.status_code == 200:
                image_list = response_data['images'][0]['id']
                return image_list

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Список ресурсов подсети
    def subnet_list(self):
        url = "https://vpc.api.cloud.yandex.net/vpc/v1/subnets"
        params = {
            "folderId": f"{self.folder_list()}"
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response_data = response.json()

            if response.status_code == 200:
                for subnet in response_data.get('subnets', []):
                    if subnet['zoneId'] == f'{self.zone_list()}':
                        return subnet['id']

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")