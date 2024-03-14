terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/ecr"
}

include "root" {
  path = find_in_parent_folders()
}

include "env" {
  path           = find_in_parent_folders("env.hcl")
  expose         = true
  merge_strategy = "no_merge"
}

inputs = {
  env             = include.env.locals.env
  project         = "sre"
  iam_roles       = ["arn:aws:iam::984119170260:user/terragrunt"]


}




dependency "roles" {
  config_path = "../roles"

}