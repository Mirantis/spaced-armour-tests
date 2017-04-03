"""
--------------------
Ironic chassis tests
--------------------
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


@pytest.mark.idempotent_id('cde24671-65b2-46f5-b8e5-e3ff087e4da6')
def test_chassis_create(create_nodes,
                        ironic_chassis_steps,
                        ironic_node_steps):
    """**Scenario:** Verify that nodes can be attached/detached from chassis.

    **Setup:**

    #. Create 3 ironic nodes

    **Steps:**

    #. Create ironic chassis_01
    #. Create ironic chassis_02
    #. Add all nodes to chassis_01
    #. Add all nodes to chassis_02
    #. Check that chassis_01 doesn't contain nodes
    #. Detach nodes from chassis 02

    **Teardown:**

    #. Delete ironic nodes
    #. Delete ironic chassis
    """
    chassis_01 = ironic_chassis_steps.create_ironic_chassis()
    chassis_02 = ironic_chassis_steps.create_ironic_chassis()

    ironic_node_steps.attach_nodes_to_chassis(create_nodes, chassis_01)
    ironic_node_steps.attach_nodes_to_chassis(create_nodes, chassis_02)

    ironic_node_steps.check_nodes_not_attached_to_chassis(create_nodes,
                                                          chassis_01)

    ironic_node_steps.detach_nodes_from_chassis(create_nodes, chassis_02)
