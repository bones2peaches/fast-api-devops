terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/rds"
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
  db_port         = 6000
  db_name         = "sre"
  iam_roles       = [dependency.roles.outputs.exec_role_arn]
  vpc_id          =dependency.vpc.outputs.vpc_id
  subnet_ids      = dependency.vpc.outputs.private_subnet_ids
  sg_id           =  dependency.sgs.outputs.rds_sg_id
  db_identifier  = "sre"
  db_user           = "api"
}


dependency "vpc" {
  config_path = "../vpc"

}

dependency "sgs" {
  config_path = "../sgs"

}

dependency "roles" {
  config_path = "../roles"
}