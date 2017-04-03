"""
--------------------------
Ironic negative node tests
--------------------------
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


@pytest.mark.idempotent_id('5a017a61-67cf-404c-bc11-1d95a4ab6cad')
@pytest.mark.parametrize("node_maintenance", [False, True])
def test_delete_nodes_in_maintenance(ironic_node_steps,
                                     node_maintenance,
                                     prepare_nodes):
    """**Scenario:** Delete nodes in maintenance.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**
    #. Set nodes to 'maintenance'
    #. Set nodes provision state to 'manage'
    #. Try to delete ironic node

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.set_maintenance(
        nodes=prepare_nodes,
        state=node_maintenance,
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_provision_state(
        nodes=prepare_nodes,
        state="manage",
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_state_bad_request(
        nodes=prepare_nodes,
        state='deleted')


@pytest.mark.idempotent_id('f4670127-81b7-472c-898b-4e7cbdda789c')
def test_boot_instances_nodes_in_maintenance(ironic_node_steps, prepare_nodes):
    """**Scenario:** Boot instances when ironic nodes in maintenance.

    **Setup:**

    #. Create 3 ironic nodes
    #. Update 3 ironic nodes
    #. Create 3 ironic ports
    #. Validate ironic nodes

    **Steps:**

    #. Set nodes to 'maintenance'
    #. Try to boot set ironic node in 'active' state

    **Teardown:**

    #. Delete 3 ironic nodes
    """
    ironic_node_steps.set_maintenance(
        nodes=prepare_nodes,
        state=True,
        timeout=config.CHANGE_NODE_STATE_TIMEOUT)

    ironic_node_steps.set_nodes_state_bad_request_maintenance(
        nodes=prepare_nodes,
        state='active')
