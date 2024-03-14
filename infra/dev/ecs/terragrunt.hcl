terraform {
  source = "git@github.com:bones2peaches/public-tf-modules.git//private-subnet-ecs/ecs"
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
    rds_secret_arn = dependency.rds.outputs.secret_arn
    vpc_id = dependency.vpc.outputs.vpc_id
    lb_subnet_ids = dependency.vpc.outputs.public_subnet_ids
    domain_name = "bones2peaches.com"
    svc_sg_id = dependency.sgs.outputs.svc_sg_id
    lb_sg_id           =  dependency.sgs.outputs.lb_sg_id
    service_subnets = dependency.vpc.outputs.private_subnet_ids
    zone_id = "Z10131012SZC70JB39WS4"
    ecr_name = dependency.ecr.outputs.ecr_name
    image_tag ="new1"
    exec_policies = [dependency.rds.outputs.kms_sm_policy_arn , dependency.ecr.outputs.pull_policy_arn]
    task_policies =[]
    db_port         = dependency.rds.outputs.db_port
    db_name         = dependency.rds.outputs.db_name
    iam_roles       = [dependency.roles.outputs.exec_role_arn]
    vpc_id          =dependency.vpc.outputs.vpc_id
    subnet_ids      = dependency.vpc.outputs.private_subnet_ids
    
    db_user           = dependency.rds.outputs.db_user
    db_hostname = dependency.rds.outputs.db_hostname
    task_role_name = dependency.roles.outputs.task_role_name
    exec_role_name = dependency.roles.outputs.task_role_name
    task_role_arn = dependency.roles.outputs.task_role_arn
    exec_role_arn = dependency.roles.outputs.task_role_arn    

    health_check_interval = 60
    health_check_path = "/api/${include.env.locals.env}/health"

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

dependency "rds" {
  config_path = "../rds"

}

dependency "ecr" {
  config_path = "../ecr"

}