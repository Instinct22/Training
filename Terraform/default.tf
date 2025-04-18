terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "0.140.1"
    }
  }
}

locals {
  folder_id = "b1gl60eill48p84ucl9p"
  cloud_id = "b1g89nen86dphk2ojdra"
}


provider "yandex" {
  cloud_id = local.cloud_id
  folder_id = local.folder_id
  service_account_key_file = "/home/kali/authorized_key.json"
}

# yandex_compute_instance.imported_vm:
resource "yandex_compute_instance" "imported_vm" {
  folder_id   = local.folder_id
  platform_id = "standard-v3"
  zone        = "ru-central1-a"

  resources {
    cores         = 2
    memory        = 2
    core_fraction = 20
  }

  boot_disk {
    auto_delete = false
    device_name = "fhml9hv2c2hoom9o4a52"
    disk_id     = "fhml9hv2c2hoom9o4a52"
    mode        = "READ_WRITE"
  }

  network_interface {
    subnet_id      = "e9bvjiqsthlru4mfq152"
    nat            = true
    ip_address     = "10.128.0.7"
  }

  metadata         = {
        "ssh-keys" = "ubuntu:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC/OpnfHNcSjEPDFdSRBJyj1YCBG59jeOchsRelZtLlaaK8Q/kZrTX/RnYrWAk4gBC2IL2IcDjI8UYv+K/nyGKU6e5oZEXQF1wTl3fBUYpcwE9vRLCNdXqtQd0K4eoFcVFivZFi5iEYukhkRqrNj1PmUc9Vr2dvO4vvBQoEE81FGyZ/dKjZvuFOAXajRJZb3yNvcIXPPgKlnQT5pwfr+HEAWDAzDFeX8xZlBfcG6i95YLrMKbHv4F66n61VwDw1+lXAzCUELFNWc0HfVg1LcQv4v4692fWtmIvF7bm2vTq9MWp2h9FczI4Zxu6hr9ppWG7dyMo37lKvYBwYN0X2Gt3DCOfIku5csBA+Z0LfAzccMMdWfyaNaw4OeU3YXrNGeKUTHbR1m0HmEHzJnD0p+sVUQiqxOkjTKeVuP1hBCjyRxtWF6nqD8JdUiIZUZbeZ4GJ5xRdkq100LqYHBZD7guAh62kpGtGMZ7TeLCOh+lUaeH05xld9gSS6dgvInb5MO10= instinct@HOME-PC"
    }

  metadata_options {
    aws_v1_http_endpoint = 1
    aws_v1_http_token    = 2
    gce_http_endpoint    = 1
    gce_http_token       = 1
  }

  scheduling_policy {
    preemptible = false
  }

  lifecycle {
    ignore_changes = [
      boot_disk,
      network_interface,
      metadata["user-data"]
    ]
  }
}

