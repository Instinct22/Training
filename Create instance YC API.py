import os
import json
import time
from turtledemo.penrose import start

from dotenv import load_dotenv
from requests import HTTPError
import requests


load_dotenv()




class YC:
    def __init__(self):
        self.iam_token = self.iam_token_create()
        self.data = {
            "iam_token": f"{self.iam_token}"
        }
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}"
        }
        self.instance_id = []



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


    # Создание instance
    def add_instance(self):
        url = "https://compute.api.cloud.yandex.net/compute/v1/instances"
        data = {
            "folderId": f"{self.folder_list()}",
            "zoneId": f"{self.zone_list()}",
            "platformId": "standard-v3",
            "resourcesSpec": {
                "memory": "2147483648",
                "cores": "2",
                "coreFraction": "20",
            },
            "bootDiskSpec": {
                "diskSpec": {
                    "size": "21474836480",
                    "imageId": f"{self.image_list()}",
                    "typeId": f"{self.disk_type_list()}"
                }
            },
            "networkInterfaceSpecs": [
                {
                    "subnetId": f"{self.subnet_list()}",
                    "primaryV4AddressSpec": {
                        "oneToOneNatSpec": {
                            "ipVersion": "IPV4"
                        }
                    }

                }


            ]
        }
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response_data = response.json()
            print(response_data)
            if response.status_code == 200:
                self.instance_id = response_data['metadata']['instanceId']
                return self.instance_id

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    def instance_get(self, timeout=600, interval=5):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}"
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                response = requests.get(url, headers=self.headers)
                response_data = response.json()

                if response.status_code == 200:
                    status = response_data['status']

                    if status == 'RUNNING':
                        print(f"Статус сервера:{status}")
                        return status

                    elif status == 'ERROR':
                        print(f"Статус сервера:{status}")
                        return status

                    time.sleep(interval)

                else:
                    print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")


if __name__ == "__main__":
    test = YC()
    test.add_instance()
    test.instance_get()

    test.revoke_token()