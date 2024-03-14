terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/roles"
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

}


