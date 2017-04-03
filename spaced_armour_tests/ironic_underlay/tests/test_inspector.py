"""
----------------------
Ironic inspector tests
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


@pytest.mark.idempotent_id('0070e720-558d-4f3d-873f-74a016e7369e')
def test_inspect_nodes(prepare_nodes, ironic_node_steps):
    """**Scenario:** Inspect ironic nodes.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Inspect ironic nodes
    #. Set nodes state 'provide'
    #. Set nodes state 'active'
    #. Get instances IP addresses
    #. Check instances are reachable via IP

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.inspect_nodes(prepare_nodes)
    ironic_node_steps.set_nodes_provision_state(
        prepare_nodes,
        state='provide',
        timeout=config.AVAILABLE_NODE_STATE_TIMEOUT)

    ironic_node_steps.boot_servers(prepare_nodes)


@pytest.mark.idempotent_id('e9925ea2-7cda-4471-8b05-d357205334bf')
def test_boot_inspect_nodes_at_the_same_time(prepare_nodes, ironic_node_steps):
    """**Scenario:** Boot instances and inspect ironic node at the same time.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set 2 nodes state 'active' at the same time set 1 node to inspect
    #. Get instances IP addresses
    #. Check instances are reachable via IP

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    inspect_node = [prepare_nodes[0]]
    boot_nodes = prepare_nodes[1:]

    ironic_node_steps.set_nodes_provision_state(boot_nodes,
                                                state='active',
                                                check=False)

    ironic_node_steps.inspect_nodes(inspect_node)

    ironic_node_steps.check_ironic_nodes_provision_state(
        boot_nodes,
        state='active',
        node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.check_ssh_connection(boot_nodes)

    ironic_node_steps.set_nodes_provision_state(
        inspect_node,
        state='provide',
        timeout=config.AVAILABLE_NODE_STATE_TIMEOUT)
