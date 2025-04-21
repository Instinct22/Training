import requests
from requests import HTTPError
import time
import socket
from Python import yc_env_config


class yc_control(yc_env_config.yc_env):

    def instance_restart(self):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}:restart"

        try:
            response = requests.post(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                return self.instance_get(target_status='RUNNING')

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Старт инстанса
    def instance_start(self):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}:start"

        try:
            response = requests.post(url, headers=self.headers)
            response_data = response.json()
            print("instance_start", response_data)

            if response.status_code == 200:
                return self.instance_get(target_status='RUNNING')

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Остановка инстанса
    def instance_stop(self):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}:stop"

        try:
            response = requests.post(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                return self.instance_get(target_status='STOPPED')

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Функция для мета информации
    def get_instance_info(self):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}"

        try:
            response = requests.get(url, headers=self.headers)
            response_data = response.json()

            if response.status_code == 200:
                self.address = response_data['networkInterfaces'][0]['primaryV4Address']['oneToOneNat']['address']

                return self.address

            else:
                print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    # Ожидание статуса развертывания инстанса
    def instance_get(self, timeout=600, interval=5, target_status=None):
        url = f"https://compute.api.cloud.yandex.net/compute/v1/instances/{self.instance_id}"
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                response = requests.get(url, headers=self.headers)
                response_data = response.json()

                if response.status_code == 200:
                    status = response_data['status']

                    if target_status is None or status == target_status:
                        print(f"Статус сервера: {status}")
                        return status

                    elif status == 'ERROR':
                        print(f"Статус сервера: {status}")
                        return status

                    time.sleep(interval)

                else:
                    print(f"Ошибка HTTP: {response.status_code}. Message: {response_data.get('message')}")
        except HTTPError as htt_err:
            print(f"Ошибка: {htt_err}")

    def check_ssh_port(self, port=22, timeout=60, interval=1):
        self.get_instance_info()
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((self.address, port), timeout=interval):
                    print(f"Порт {port} на {self.address} доступен для подключения.")
                    return True
            except (socket.timeout, socket.error) as e:
                print(f"Ошибка подключения к порту {port} на {self.address}: {e}.")
                time.sleep(interval)

        print(f"Ошибка: Порт {port} на {self.address} не доступен для подключения в течение {timeout} секунд.")
        return False