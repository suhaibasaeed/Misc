#!/usr/bin/env python
from nornir_napalm.plugins.tasks import napalm_ping, napalm_get


def verify_l2(task):
    """Nornir custom task - ping interfaces for verification"""
    ping_list = []
    # Extract IP addr of intfs to ping from host obj
    for k, v in task.host["interfaces"].items():
        ping_list.append(v["ipaddr"])

    for ip in ping_list:
        task.run(task=napalm_ping, dest=ip)


def verify_bgp_peers(task):
    """Nornir custom task - Verify 2 BGP peers"""
    result = task.run(task=napalm_get, getters=["bgp_neighbors"])

    established_peers = 0
    for peer, value in result[0].result["bgp_neighbors"]["global"]["peers"].items():
        if value["is_up"]:
            established_peers += 1

    if established_peers == 2:
        return "2 BGP peers are Established"
    else:
        return f"BGP peer/s down"
