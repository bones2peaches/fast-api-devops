# Generated by Terragrunt. Sig: nIlQXj57tbuaRZEa
provider "aws" {
  region  = "us-east-1"
  profile = "dylan"
  
  assume_role {
    session_name = "leson-160"
    role_arn = "arn:aws:iam::984119170260:role/terraform-role"
  }
}