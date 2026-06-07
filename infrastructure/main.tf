terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

# Connect to the local Docker daemon
provider "docker" {}

# Pull a lightweight Alpine Linux image for testing
resource "docker_image" "alpine" {
  name         = "alpine:latest"
  keep_locally = true
}

# 🔴 NON-COMPLIANT CONTAINER (Runs as root)
resource "docker_container" "non_compliant_app" {
  name    = "non_compliant_app"
  image   = docker_image.alpine.image_id
  command = ["sleep", "infinity"] # Keeps the container running
}

# 🟢 COMPLIANT CONTAINER (Runs as user 1000)
resource "docker_container" "compliant_app" {
  name    = "compliant_app"
  image   = docker_image.alpine.image_id
  command = ["sleep", "infinity"]
  user    = "1000"
}
