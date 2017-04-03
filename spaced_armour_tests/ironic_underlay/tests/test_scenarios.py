"""
----------------------
Ironic scenarios tests
----------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from spaced_armour_tests.ironic_underlay import config

from third_party import utils


@pytest.mark.idempotent_id('6492f39a-cceb-4bf9-aaff-27b123366ccc')
def test_enroll_nodes(ironic_node_steps, prepare_nodes):
    """**Scenario:** Enroll ironic nodes boot instances.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set nodes state 'active'
    #. Get instances IP addresses
    #. Check instances are reachable via IP

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.boot_servers(prepare_nodes)


@pytest.mark.idempotent_id('8ba5c32a-8b1d-4006-86c1-3827d33b9229')
@pytest.mark.parametrize("node_maintenance", [True, False])
def test_change_nodes_power_state_maintenance(ironic_node_steps,
                                              prepare_nodes,
                                              node_maintenance):
    """**Scenario:** Test changing ironic nodes power states and maintenance.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set nodes state 'active'
    #. Check instances are reachable via IP
    #. Get instances IP addresses
    #. Set nodes to 'maintenance'
    #. Set nodes power state to 'off'
    #. Set nodes power state to 'on'
    #. Check SSH connection

    **Teardown:**

    #. Delete 3 ironic nodes
    """

    ironic_node_steps.boot_servers(prepare_nodes)

    ironic_node_steps.set_maintenance(
        nodes=prepare_nodes,
        state=node_maintenance,
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_ironic_nodes_power_state(
        nodes=prepare_nodes,
        state='off',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_ironic_nodes_power_state(
        nodes=prepare_nodes,
        state='on',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.check_ssh_connection(nodes=prepare_nodes)


@pytest.mark.idempotent_id('078a29c0-f420-4414-bfed-43987c94526f')
@pytest.mark.parametrize("node_maintenance", [False, True])
def test_change_nodes_provisioning_state_maintenance(ironic_node_steps,
                                                     prepare_nodes,
                                                     node_maintenance):
    """**Scenario:** Change node provision state while it is in maintenance.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**
    #. Set nodes to 'maintenance'
    #. Set nodes provision state to 'manage'
    #. Set nodes provision state to 'inspect'
    #. Set nodes provision state to 'provide'

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.set_maintenance(
        nodes=prepare_nodes,
        state=node_maintenance,
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_provision_state(
        nodes=prepare_nodes,
        state='manage',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_provision_state(
        nodes=prepare_nodes,
        state='inspect',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_provision_state(
        nodes=prepare_nodes,
        state='provide',
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)


@pytest.mark.idempotent_id('b3c476ba-d2f6-404b-8961-d8347818c930')
def test_rebuild_nodes(ironic_node_steps,
                       prepare_nodes):
    """**Scenario:** Rebuild ironic nodes.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set node state 'active'
    #. Get instance IP address
    #. Check if instance is reachable via IP
    #. Set ironic nodes state 'active'
    #. Check ironic nodes provision state
    #. Get instances IP addresses
    #. Check instances are reachable via IP
    #. Set node state 'rebuild'
    #. Check ironic nodes state is `active`
    #. Get instance IP addresses
    #. Check if instance is reachable via IP

    **Teardown:**

    #. Delete ironic node
    """
    ironic_node_steps.boot_servers(prepare_nodes)

    ironic_node_steps.set_nodes_provision_state(
        prepare_nodes,
        state='rebuild',
        check=False)

    ironic_node_steps.check_ironic_nodes_provision_state(
        prepare_nodes,
        state='active',
        node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ip_address = ironic_node_steps.get_instance_ipv4_addresses(prepare_nodes)

    utils.ssh_connection(ipv4_addresses=ip_address,
                         username=config.IMAGE_USERNAME,
                         password=config.IMAGE_PASSWORD,
                         timeout=config.SSH_TIMEOUT)
