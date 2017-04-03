"""
--------------------------
Ironic node cleaning tests
--------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from spaced_armour_tests.ironic_underlay import config
from third_party.utils import ssh_connection


@pytest.mark.idempotent_id('de64a66b-5bb5-4c79-a8a4-cf486c007dae')
def test_cleaning_nodes(ironic_node_steps,
                        prepare_nodes,
                        nodes_config,
                        ironic_port_steps,
                        port_steps):
    """**Scenario:** Test to check cleaning of ironic nodes.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set nodes state 'active'
    #. Get instances IP addresses
    #. Check instances are reachable via IP
    #. Set nodes provision state `deleted`
    #. Set nodes provision state `manage`
    #. Clean nodes
    #. Check ironic nodes provision state `clean wait`
    #. Set ironic nodes maintenance to `True`
    #. Get ironic ports MAC addresses
    #. Get fixed IP addresses
    #. Check instances are reachable via SSH by IP address
    #. Set ironic nodes maintenance to `False`
    #. Check ironic nodes provision state `clean wait`
    #. Check ironic nodes provision state `manage`

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.boot_servers(prepare_nodes)

    ironic_node_steps.set_nodes_provision_state(
        prepare_nodes,
        state='deleted',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_provision_state(
        prepare_nodes,
        state='manage',
        check=False,
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.clean_nodes(
        prepare_nodes,
        cleansteps=config.CLEANSTEPS,
        timeout=config.CLEANING_NODES_TIMEOUT,
        check=False)

    ironic_node_steps.check_ironic_nodes_provision_state(
        prepare_nodes,
        state='clean wait',
        node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_maintenance(prepare_nodes, state=True)

    mac_addresses = ironic_port_steps.get_ports_mac_addresses(nodes_config)

    ip_addresses = []
    for mac in mac_addresses:
        port = port_steps.get_port(mac_address=mac)
        ip_addresses.append(port['fixed_ips'][0]['ip_address'])

    ssh_connection(ipv4_addresses=ip_addresses,
                   username=config.ANSIBLE_IMAGE_USERNAME,
                   password=config.ANSIBLE_IMAGE_PASSWORD,
                   timeout=config.SSH_TIMEOUT)

    ironic_node_steps.set_maintenance(prepare_nodes, state=False, check=False)

    ironic_node_steps.check_ironic_nodes_provision_state(
        prepare_nodes,
        state='clean wait',
        node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.check_ironic_nodes_provision_state(
        prepare_nodes,
        state='manage',
        node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)
