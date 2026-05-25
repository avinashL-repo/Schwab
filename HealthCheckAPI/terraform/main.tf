terraform {
  required_providers {

    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }

  }
}

provider "docker" {}

# ---------------------------------------------------
# DOCKER IMAGE
# ---------------------------------------------------

resource "docker_image" "health_api_image" {
  name = "healthcheckapi:latest"
}

# ---------------------------------------------------
# DOCKER CONTAINER
# ---------------------------------------------------

resource "docker_container" "health_api_container" {

  name  = "healthcheckapi-container"
  image = docker_image.health_api_image.image_id

  ports {
    internal = 8000
    external = 8000
  }

}