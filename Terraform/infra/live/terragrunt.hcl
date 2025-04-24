locals {
  cloud_id    = "b1g89nen86dphk2ojdra"
  folder_id   = "b1gl60eill48p84ucl9p"
  subnet_id   = "e9bvjiqsthlru4mfq152"
  image_id    = "fd833ivvmqp6cuq7shpc"
  block_size  = 4096
  size        = 50
  type        = "network-hdd"
  zone        = "ru-central1-a"
  platform_id = "standard-v3"
  service_account_key_file = "/home/kali/authorized_key.json"
}

inputs = local