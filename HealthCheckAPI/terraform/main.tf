terraform {
  required_version = ">= 1.0"
}

provider "local" {}

resource "local_file" "example" {
  filename = "terraform-demo.txt"
  content  = "Terraform setup successful"
}