import os
import json
import random
from time import sleep, time

import names
import subprocess

from dotenv import load_dotenv
from requests import HTTPError
import requests
from yc_instance_control import yc_control

load_dotenv()




class yc_manager(yc_control):
    def __init__(self):
        super().__init__()

    # Создание instance
    def add_instance(self):
        url = "https://compute.api.cloud.yandex.net/compute/v1/instances"

        with open("set-passwd.yaml", "r") as f:
            cloud_init_data = f.read()

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
            ],
            "metadata": {
                "user-data": cloud_init_data
            }
        }
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            response_data = response.json()

            if response.status_code == 200:
                self.instance_id = response_data['metadata']['instanceId']
                return self.instance_get(target_status='RUNNING'), self.instance_id

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Обновления параметров для инстанса
    def instance_update(self):
        instance_name = f"vm-{names.get_first_name().lower()}-{random.randint(100, 999)}"

        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}"
        data = {
            "updateMask": "labels,name",
            "name": instance_name,
            "labels": {
                "environment": "prod"
            },
        }

        try:
            response = requests.patch(url, headers=self.headers, json=data)
            response_data = response.json()

            if response.status_code == 200:

                return

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Установка nginx
    def install_nginx(self):
        self.check_ssh_port()

        commands = [
            'sudo apt update',
            'sudo apt install -y nginx',
            'sudo systemctl start nginx',
            'sudo systemctl enable nginx',
            'echo "Nginx установлен"'
        ]
        remote_commands_str = ";".join(commands)

        try:
            subprocess.run([
                'ssh',
                '-i', os.getenv("key_path"),
                '-o', 'StrictHostKeyChecking=no',
                f'{os.getenv("remote_user")}@{self.get_instance_info()}',
                remote_commands_str
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Ошибка: {e}")



if __name__ == "__main__":
    test = yc_manager()
    test.add_instance()
    test.instance_update()
    test.install_nginx()


    test.revoke_token()