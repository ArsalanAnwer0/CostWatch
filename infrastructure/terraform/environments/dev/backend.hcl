bucket         = "costwatch-terraform-state-dev"
key            = "dev/terraform.tfstate"
region         = "us-west-2"
dynamodb_table = "costwatch-terraform-locks-dev"
encrypt        = true