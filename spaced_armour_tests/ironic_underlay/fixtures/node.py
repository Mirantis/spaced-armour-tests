"""
--------------------
Ironic node fixtures
--------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from spaced_armour_tests.ironic_underlay import config
from spaced_armour_tests.ironic_underlay.fixtures.port import ironic_port_steps  # noqa
from spaced_armour_tests.ironic_underlay import steps


__all__ = [
    'get_ironic_node_steps',
    'unexpected_node_cleanup',
    'ironic_node_steps',
    'cleanup_nodes',
    'primary_nodes',
    'ironic_node',
    'nodes_config',
    'prepare_nodes',
    'create_nodes',
]


@pytest.fixture(scope='session')
def get_ironic_node_steps(get_ironic_client):
    """Callable session fixture to get ironic steps.

    Args:
        get_ironic_client (function): function to get ironic client

    Returns:
        function: function to instantiated ironic steps
    """
    def _get_ironic_node_steps(**credentials):
        return steps.IronicNodeSteps(
            get_ironic_client(**credentials))

    return _get_ironic_node_steps


@pytest.fixture
def unexpected_node_cleanup(primary_nodes,
                            get_ironic_node_steps,
                            cleanup_nodes):
    """Function fixture to clear unexpected volumes.

    It provides cleanup before and after test.
    """
    if config.CLEANUP_UNEXPECTED_BEFORE_TEST:
        cleanup_nodes(get_ironic_node_steps())

    yield

    if config.CLEANUP_UNEXPECTED_AFTER_TEST:
        cleanup_nodes(get_ironic_node_steps())


@pytest.fixture
def ironic_node_steps(unexpected_node_cleanup,
                      get_ironic_node_steps,
                      cleanup_nodes):
    """Callable function fixture to get ironic steps.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Args:
        get_ironic_node_steps (function): function to get ironic steps
        cleanup_nodes (function): function to cleanup nodes after test

    Yields:
        IronicNodeSteps: instantiated ironic node steps
    """
    _node_steps = get_ironic_node_steps()

    nodes_before = _node_steps.get_ironic_nodes(check=False)
    nodes_uuids_before = {node.uuid for node in nodes_before}

    yield _node_steps
    cleanup_nodes(_node_steps,
                  uncleanable_nodes_uuids=nodes_uuids_before)


@pytest.fixture(scope='session')
def cleanup_nodes(uncleanable):
    """Callable session fixture to cleanup nodes.

    Args:
        uncleanable (AttrDict): Data structure with skipped resources
    """

    def _cleanup_nodes(_nodes_steps,
                       limit=0,
                       uncleanable_nodes_uuids=None):
        uncleanable_nodes_uuids = (uncleanable_nodes_uuids or
                                   uncleanable.nodes_ids)
        deleting_nodes = []

        for node in _nodes_steps.get_ironic_nodes(check=False):
            if node.uuid not in uncleanable_nodes_uuids:
                deleting_nodes.append(node)

        if len(deleting_nodes) > limit:
            _nodes_steps.delete_ironic_nodes(deleting_nodes)

    return _cleanup_nodes


@pytest.fixture
def primary_nodes(get_ironic_node_steps,
                  cleanup_nodes,
                  uncleanable):
    """Function fixture to remember primary nodes before tests.

    Also optionally in finalization it deletes all unexpected nodes which
    are remained after tests.

    Args:
        get_ironic_node_steps (function): Function to get ironic steps.
        cleanup_nodes (function): Function to cleanup volumes.
        uncleanable (AttrDict): Data structure with skipped resources.
    """
    nodes_before = set()
    for node in get_ironic_node_steps().get_ironic_nodes(check=False):
        nodes_before.add(node)
        uncleanable.nodes_ids.add(node.uuid)

    yield
    if config.CLEANUP_UNEXPECTED_AFTER_ALL:
        cleanup_nodes(get_ironic_node_steps(),
                      uncleanable_nodes_uuids=nodes_before)


@pytest.fixture
def ironic_node(ironic_node_steps):
    """Function fixture to create ironic node with default options.

    Args:
        ironic_node_steps(function): function to get ironic steps

    Returns:
        object: ironic node
    """
    return ironic_node_steps.create_ironic_nodes()[0]


@pytest.fixture
def nodes_config():
    """Function fixture to get ironic nodes configuration.

    Returns:
        dict: nodes_config dictionary
    """
    nodes_config = {}

    for node in config.NODES_INFO:
        nodes_config.update({node: {}})
        nodes_config[node].update({'node_driver_info': {}})
        nodes_config[node].update({'node_mac': {}})

        nodes_config[node].update({
            'node_driver_info':
                config.NODES_INFO[node]['driver_info']['power']})
        nodes_config[node]['node_driver_info'].update({
            'deploy_kernel': config.DEPLOY_KERNEL_IMAGE})
        nodes_config[node]['node_driver_info'].update({
            'deploy_ramdisk': config.DEPLOY_RAMDISK_IMAGE})

        nodes_config[node].update({
            'node_mac': config.NODES_INFO[node]['nics'][0]['mac']})

    return nodes_config


@pytest.fixture
def create_nodes(ironic_node_steps, ironic_port_steps, nodes_config):
    """Function fixture to create ironic nodes.

    #. Create ironic nodes

    Returns:
        list of objects: ironic nodes
    """
    nodes = []

    for node_info in nodes_config:
        node = ironic_node_steps.create_ironic_nodes(
            driver='pxe_ipmitool_ansible',
            driver_info=nodes_config[node_info]['node_driver_info'])[0]

        ironic_port_steps.create_ports(
            node,
            addresses=[nodes_config[node_info]['node_mac']])

        nodes.append(node)

    return nodes


@pytest.fixture
def prepare_nodes(create_nodes, ironic_node_steps):
    """Function fixture to prepare ironic nodes.

    #. Update ironic nodes
    #. Validate ironic nodes
    #. Check that nodes reach 'available' provision state

    Returns:
        list of objects: ironic nodes
    """
    ironic_node_steps.update_nodes(nodes=create_nodes,
                                   patch=config.NODE_PATCH)
    ironic_node_steps.set_nodes_provision_state(
        nodes=create_nodes,
        state='manage',
        timeout=config.AVAILABLE_NODE_STATE_TIMEOUT)
    ironic_node_steps.set_nodes_provision_state(
        nodes=create_nodes,
        state='provide',
        timeout=config.AVAILABLE_NODE_STATE_TIMEOUT)

    return create_nodes
