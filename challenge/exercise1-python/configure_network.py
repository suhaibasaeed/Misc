#!/usr/bin/env python
from nornir import InitNornir
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_utils.plugins.functions import print_result
from verify import verify_l2, verify_bgp_peers


def read_yaml(task):
    """Nornir custom task - reads in data from file and stores in host obj"""
    in_yaml = task.run(task=load_yaml, file="input.yml")

    # Store yaml data in host object so it's persistent for use in next task
    task.host.data = in_yaml.result[task.host.name]


def render_configs(task, template_name):
    """Nornir custom task - Render j2 template"""
    template_path = "./templates"
    result = task.run(
        task=template_file, template=template_name, path=template_path, **task.host
    )
    # Store rendered config in host object for use in future tasks
    task.host[f"{template_name.strip('.j2')}_config"] = result[0].result


def write_configs(task, config):
    """Write config to disk for review - 2nd arg is which config i.e. bgp/interfaces"""
    hostname = task.host.name
    filename = f"configs/{hostname}/{hostname}_{config}.conf"
    content = task.host[f"{config}_config"]

    task.run(task=write_file, filename=filename, content=content)


def deploy_configs(task, config):
    """Nornir custom task - Push config to device via NAPALM - 2nd arg is same as above"""
    hostname = task.host.name
    filename = f"configs/{hostname}/{hostname}_{config}.conf"

    with open(filename, "r") as f:
        cfg = f.read()

    task.run(task=napalm_configure, configuration=cfg)


def main():
    """main function"""

    # Initialise Nornir
    nr = InitNornir("config.yml")
    # Run task to read in yaml file
    yaml_results = nr.run(task=read_yaml)
    print_result(yaml_results)
    # Run tasks to render, write and deploy interfaces config
    render_int_results = nr.run(task=render_configs, template_name="interfaces.j2")
    print_result(render_int_results)

    write_int_results = nr.run(task=write_configs, config="interfaces")
    print_result(write_int_results)

    deploy_int_results = nr.run(task=deploy_configs, config="interfaces")
    print_result(deploy_int_results)
    # Run verify L2 task
    l2_results = nr.run(task=verify_l2)
    print_result(l2_results)

    # Run tasks to render, write and deploy interfaces config
    render_bgp_results = nr.run(task=render_configs, template_name="bgp.j2")
    print_result(render_bgp_results)

    write_bgp_results = nr.run(task=write_configs, config="bgp")
    print_result(write_bgp_results)

    deploy_bgp_results = nr.run(task=deploy_configs, config="bgp")
    print_result(deploy_bgp_results)
    # Run task to verify BGP peers
    verify_bgp_results = nr.run(task=verify_bgp_peers)
    print_result(verify_bgp_results)


if __name__ == "__main__":

    main()
