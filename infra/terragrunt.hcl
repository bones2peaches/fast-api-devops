remote_state {
  backend = "s3"
  generate = {
    path      = "state.tf"
    if_exists = "overwrite_terragrunt"
  }

  config = {
    profile = "dylan"
    role_arn = "arn:aws:iam::984119170260:role/terraform-role"
    bucket = "terragrunt-aws-sre"

    key = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
  }
}

generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"

  contents = <<EOF
provider "aws" {
  region  = "us-east-1"
  profile = "dylan"
  
  assume_role {
    session_name = "leson-160"
    role_arn = "arn:aws:iam::984119170260:role/terraform-role"
  }
}
EOF
}