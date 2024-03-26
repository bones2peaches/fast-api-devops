terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/vpce"
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
  vpc_id          =dependency.vpc.outputs.vpc_id
  subnet_ids      = dependency.vpc.outputs.private_subnet_ids
  sg_id           =  dependency.sgs.outputs.vpce_sg_id
  route_table_ids = [dependency.vpc.outputs.private_rt_id]
}


dependency "vpc" {
  config_path = "../vpc"

}

dependency "sgs" {
  config_path = "../sgs"


}