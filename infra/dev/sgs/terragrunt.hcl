terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/sgs"
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
  app_port =        5000
  vpc_id          =dependency.vpc.outputs.vpc_id
}


dependency "vpc" {
  config_path = "../vpc"


}