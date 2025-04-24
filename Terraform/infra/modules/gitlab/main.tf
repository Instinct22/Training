terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "0.140.1"
    }
  }
}

provider "yandex" {
  cloud_id           = var.cloud_id
  folder_id          = var.folder_id
  service_account_key_file = var.service_account_key_file
}

resource "yandex_compute_instance" "gitlab" {
  folder_id   = var.folder_id
  platform_id = var.platform_id
  zone        = var.zone
  name        = "gitlab"

  resources {
    cores  = 4
    memory = 8
  }

  boot_disk {
    initialize_params {
      block_size = var.block_size
      image_id   = var.image_id
      size       = var.size
      type       = var.type
    }
  }

  network_interface {
    subnet_id = var.subnet_id
    nat       = true
  }

  metadata = {
    user-data = file("cloud-init.yaml")
  }
}

