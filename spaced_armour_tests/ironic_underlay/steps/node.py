"""
-----------------
Ironic node steps
-----------------
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
import time

from hamcrest import equal_to, assert_that, is_not, empty, has_key, contains_inanyorder, matches_regexp  # noqa

from ironicclient import exceptions

from spaced_armour_tests.ironic_underlay import config
from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import utils
from stepler.third_party import waiter

from third_party.utils import ssh_connection

__all__ = [
    'IronicNodeSteps'
]


class IronicNodeSteps(BaseSteps):
    """Node steps."""

    @steps_checker.step
    def create_ironic_nodes(self,
                            driver='fake',
                            nodes_names=None,
                            count=1,
                            check=True,
                            **kwargs):
        """Step to create a ironic node.

        Args:
            driver (string): The name or UUID of the driver.
            nodes_names (list): names of created images, if not specified
                one image name will be generated.
            count (int): count of created chassis, it's ignored if
                chassis_descriptions are specified; one chassis is created if
                both args are missing.
            check (string): For checking node presence
            **kwargs (optional): A dictionary containing the attributes
            of the resource that will be created:
                chassis_uuid - The uuid of the chassis.
                driver_info - The driver info.
                extra - Extra node parameters.
                uuid - The uuid of the node.
                properties - Node properties.
                name - The name of the node.
                network_interface - The network interface of the node.
                resource_class - The resource class of the node.

        Raises:
             TimeoutExpired: if check failed after timeout.

        Returns:
            list: list of objects.
        """
        nodes_names = nodes_names or utils.generate_ids(count=count)
        nodes_list = []
        _nodes_names = {}

        for name in nodes_names:
            node = self._client.node.create(driver=driver, name=name, **kwargs)

            _nodes_names[node.uuid] = name
            nodes_list.append(node)

        if check:
            self.check_ironic_nodes_presence(nodes_list)
            for node in nodes_list:
                assert_that(_nodes_names[node.uuid], equal_to(node.name))

        return nodes_list

    @steps_checker.step
    def delete_ironic_nodes(self, nodes, check=True):
        """Step to delete node.

        Args:
            nodes (list): list of ironic nodes.
            check (bool): flag whether to check step or not.
        """
        for node in nodes:
            node = self._get_node(node.uuid)

            if node.provision_state not in (
                    'available', 'manageable', 'enroll', 'adopt failed'):
                self.set_nodes_provision_state([node],
                                               state='deleted',
                                               check=False)

            if node.power_state not in ('None', 'off'):
                self.set_ironic_nodes_power_state([node], state='off')

            self._client.node.delete(node.uuid)

        if check:
            self.check_ironic_nodes_presence(nodes, must_present=False)

    @steps_checker.step
    def check_ironic_nodes_presence(self,
                                    nodes,
                                    must_present=True,
                                    node_timeout=0):
        """Verify step to check ironic node is present.

        Args:
            nodes (list): list of ironic nodes.
            must_present (bool): flag whether node should present or not.
            node_timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        expected_presence = {node.uuid: must_present for node in nodes}

        def _check_ironic_nodes_presence():
            actual_presence = {}

            for node in nodes:
                try:
                    self._client.node.get(node.uuid)
                    actual_presence[node.uuid] = True
                except exceptions.NotFound:
                    actual_presence[node.uuid] = False

            return waiter.expect_that(actual_presence,
                                      equal_to(expected_presence))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_nodes_presence, timeout_seconds=timeout)

    @steps_checker.step
    def set_maintenance(self,
                        nodes,
                        state,
                        reason=None,
                        check=True,
                        timeout=0):
        """Set the maintenance mode for the nodes.

        Args:
            nodes (list): The list of ironic nodes.
            state (Bool): the maintenance mode; either a Boolean or a string
                representation of a Boolean (eg, 'true', 'on', 'false',
                'off'). True to put the node in maintenance mode; False
                to take the node out of maintenance mode.
            reason (string): Optional string. Reason for putting node
                into maintenance mode.
            check (bool): flag whether to check step or not.
            timeout (int): seconds to wait a result of check.

        Raises:
            InvalidAttribute: if state is an invalid string.
        """
        for node in nodes:
            self._client.node.set_maintenance(node_id=node.uuid,
                                              state=state,
                                              maint_reason=reason)
        if check:
            self.check_ironic_nodes_maintenance(nodes=nodes,
                                                state=state,
                                                node_timeout=timeout)

    @steps_checker.step
    def check_ironic_nodes_maintenance(self,
                                       nodes,
                                       state,
                                       node_timeout=0):
        """Check ironic node maintenance was changed.

        Args:
            nodes (list): The list of ironic nodes.
            state (Bool): the maintenance mode; either a Boolean or a string
                representation of a Boolean (eg, 'true', 'on', 'false',
                'off'). True to put the node in maintenance mode; False
                to take the node out of maintenance mode.
            node_timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        expected_maintenance = {node.uuid: state for node in nodes}

        def _check_ironic_node_maintenance():
            actual_maintenance = {}
            for node in nodes:
                try:
                    node = self._get_node(node.uuid)
                    actual_maintenance[node.uuid] = node.maintenance
                except exceptions.NotFound:
                    actual_maintenance[node.uuid] = None

            return waiter.expect_that(actual_maintenance,
                                      equal_to(expected_maintenance))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_node_maintenance, timeout_seconds=timeout)

    @steps_checker.step
    def set_ironic_nodes_power_state(self,
                                     nodes,
                                     state,
                                     check=True,
                                     timeout=0):
        """Set the power state for the node.

        Args:
            nodes (list): The list of ironic nodes.
            state (string): the power state mode; `on` to put the node in power
                state mode on; `off` to put the node in power state mode off;
                `reboot` to reboot the node.
            check (bool): flag whether to check step or not.
            timeout (int): seconds to wait a result of changing state.

        Raises:
            InvalidAttribute: if state is an invalid string.
        """
        for node in nodes:
            self._client.node.set_power_state(node_id=node.uuid, state=state)

        if check:
            self.check_ironic_nodes_power_state(nodes=nodes,
                                                state=state,
                                                node_timeout=timeout)

    @steps_checker.step
    def check_ironic_nodes_power_state(self,
                                       nodes,
                                       state,
                                       node_timeout=0):
        """Check ironic node power state was changed.

        Args:
            nodes (list): The list of ironic nodes.
            state (string): the power state mode; `on` to put the node in power
                state mode on; `off` to put the node in power state mode off;
                `reboot` to reboot the node.
            node_timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        target_state = state

        if target_state == 'off':
            time.sleep(config.REBOOT_TIMEOUT)
            expected_state = 'power off'
        elif target_state == 'on':
            expected_state = 'power on'
        elif target_state == 'soft off':
            expected_state = 'power off'
        elif target_state == 'reboot':
            time.sleep(config.REBOOT_TIMEOUT)
            expected_state = 'power on'
        elif target_state == 'soft reboot':
            time.sleep(config.REBOOT_TIMEOUT)
            expected_state = 'power on'
        else:
            expected_state = target_state

        expected_power_state = {node.uuid: expected_state for node in nodes}

        def _check_ironic_nodes_power_state():
            actual_power_state = {}
            for node in nodes:
                try:
                    node = self._get_node(node.uuid)
                    actual_power_state[node.uuid] = node.power_state

                except exceptions.NotFound:
                    actual_power_state[node.uuid] = None

            return waiter.expect_that(actual_power_state,
                                      equal_to(expected_power_state))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_nodes_power_state, timeout_seconds=timeout)

    def _get_node(self, node_uuid):
        return self._client.node.get(node_uuid)

    @steps_checker.step
    def get_ironic_nodes(self, check=True, **kwargs):
        """Step to retrieve nodes.

        Args:
            check (bool): flag whether to check step or not.

        Returns:
            list of objects: list of nodes.
            **kwargs: like: {'name': 'test_node', 'status': 'active'}

        Raises:
            AssertionError: if nodes collection is empty.
        """
        nodes = self._client.node.list(**kwargs)

        if kwargs:
            matched_nodes = []
            for node in nodes:
                node_dict = node.to_dict()
                for key, value in kwargs.items():
                    if not (key in node_dict and node_dict[key] == value):
                        break
                else:
                    matched_nodes.append(node)

            nodes = matched_nodes

        if check:
            assert_that(nodes, is_not(empty()))

        return nodes

    @steps_checker.step
    def get_ironic_node(self, node, check=True):
        """Get node by provided uuid.

        Args:
            node (obj): ironic node.
            check (bool): flag whether to check step or not.

        Returns:
            object: ironic node.

        Raises:
            AssertionError: if node wasn't found.
        """
        node = self._client.node.get(node_id=node.uuid)

        if check:
            assert_that(node, is_not(empty()))

        return node

    @steps_checker.step
    def get_instance_ipv4_addresses(self, nodes, check=True):
        """Get instance ipv4 address.

        Args:
            nodes (list): list of objects ironic nodes.
            check (bool): flag whether to check step or not.

        Returns:
            list: ipv4_addresses.

        Raises:
            ValueError: if ipv4 addresses list is empty.
        """
        ipv4_addresses = []

        for node in nodes:
            node = self.get_ironic_node(node=node)
            ipv4_address = node.instance_info['ipv4_address']
            ipv4_addresses.append(ipv4_address)

            if check:
                assert_that(ipv4_address, is_not(empty()))

        return ipv4_addresses

    @steps_checker.step
    def check_ironic_nodes_provision_state(self,
                                           nodes,
                                           state,
                                           node_timeout=0):
        """Check ironic node provision state was changed.

        Args:
            nodes (list): the list of ironic nodes.
            state (string): the provision state mode.
            node_timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """

        target_state = state
        if target_state == 'deleted':
            expected_state = 'available'

        elif target_state == 'provide':
            expected_state = 'available'

        elif target_state == 'manage':
            expected_state = 'manageable'

        elif target_state == 'inspect':
            expected_state = 'manageable'

        else:
            expected_state = target_state

        expected_provision_state = {
            node.uuid: expected_state for node in nodes}

        def _check_ironic_nodes_provision_state():
            actual_provision_state = {}

            for node in nodes:
                try:
                    node = self._get_node(node.uuid)
                    actual_provision_state[node.uuid] = node.provision_state

                except exceptions.NotFound:
                    actual_provision_state[node.uuid] = None

            return waiter.expect_that(actual_provision_state,
                                      equal_to(expected_provision_state))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_nodes_provision_state,
                    timeout_seconds=timeout)

    @steps_checker.step
    def get_node_by_instance_uuid(self, server_uuid, check=True):
        """Step to get node by instance uuid.

        Args:
            server_uuid (string): the uuid of the nova server.
            check (bool): flag whether to check step or not.

        Returns:
            object: ironic node.

        Raises:
            AssertionError: if node is empty.
        """
        node = self._client.node.get_by_instance_uuid(server_uuid)

        if check:
            assert_that(node.instance_uuid, equal_to(server_uuid))

        return node

    @steps_checker.step
    def check_ironic_nodes_attribute_value(self,
                                           nodes,
                                           attribute,
                                           expected_value,
                                           node_timeout=0):
        """Check ironic nodes attribute value.

        Args:
            nodes (list): the list of ironic nodes.
            attribute (string): the node attribute.
            expected_value (string): the value of the node attribute.
            node_timeout (int): seconds to wait a result of check.

        Raises:
            TimeoutExpired: if check failed after timeout.
        """
        expected_attribute_value = {node.uuid:
                                    expected_value for node in nodes}

        def _check_ironic_nodes_attribute_value():
            actual_attribute_value = {}
            for node in nodes:
                try:
                    self._get_node(node.uuid)
                    actual_attribute_value[node.uuid] = getattr(node,
                                                                attribute)

                except exceptions.NotFound:
                    actual_attribute_value[node.uuid] = None

            return waiter.expect_that(actual_attribute_value,
                                      equal_to(expected_attribute_value))

        timeout = len(nodes) * node_timeout
        waiter.wait(_check_ironic_nodes_attribute_value,
                    timeout_seconds=timeout)

    @steps_checker.step
    def update_nodes(self, nodes, patch, check=True):
        """Step to update node.

        Args:
            nodes (list): the list of ironic nodes.
            patch (list): the list of  items to update.
            check (bool): flag whether to check step or not.

        Raises:
            AssertionError: if node wasn't updated.
        """
        for node in nodes:
            self._client.node.update(node_id=node.uuid, patch=patch)

        if check:
            for node in nodes:
                self._get_node(node.uuid)
                item_to_update = patch[0]['path'].split('/')[1]

                assert_that(node.to_dict(), has_key(item_to_update))

    @steps_checker.step
    def validate_nodes(self, nodes):
        """Step to validate nodes.

        Args:
            nodes (list): the list of objects ironic nodes.

        Raises:
            AssertionError: if node is not ready.
        """
        for node in nodes:
            node_status = self._client.node.validate(node_uuid=node.uuid)

            assert_that(node_status.boot['result'] is True)
            assert_that(node_status.deploy['result'] is True)
            assert_that(node_status.management['result'] is True)
            assert_that(node_status.network['result'] is True)
            assert_that(node_status.power['result'] is True)

    @steps_checker.step
    def inspect_nodes(self, nodes, check=True):
        """Step to inspect nodes.

        Args:
            nodes (list): the list of objects ironic nodes.
            check (bool): flag whether to check step or not.

        Raises:
            AssertionError: if node is not ready.
        """
        self.set_nodes_provision_state(nodes, state='manage', check=False)
        self.check_ironic_nodes_provision_state(nodes, state='manageable')

        current_properties = {node.uuid: node.properties for node in nodes}
        for prop in current_properties.values():
            assert_that(prop.keys(), empty())

        self.set_nodes_provision_state(
            nodes,
            state='inspect',
            check=True,
            timeout=config.CHANGE_NODE_STATE_TIMEOUT)
        if check:
            expected_properties = {}
            for node in nodes:
                node = self._get_node(node.uuid)
                expected_properties[node.uuid] = node.properties

            for prop in expected_properties.values():
                assert_that(prop.keys(), contains_inanyorder('memory_mb',
                                                             'cpu_arch',
                                                             'local_gb',
                                                             'cpus',
                                                             'capabilities'))

    @steps_checker.step
    def set_nodes_provision_state(self, nodes, state, check=True, timeout=0):
        """Step to set provision state for the nodes.

        Args:
            nodes (list): the list of ironic nodes.
            state (string): The desired provision state. One of 'active',
                'deleted', 'rebuild', 'inspect', 'provide', 'manage', 'clean',
                'abort'.
            check (bool): flag whether to check step or not.
            timeout (int): seconds to wait a result of change state.

        Raises:
            AssertionError: if state wasn't applied.
        """
        for node in nodes:
            self._client.node.set_provision_state(node_uuid=node.uuid,
                                                  state=state)
        if check:
            self.check_ironic_nodes_provision_state(nodes=nodes,
                                                    state=state,
                                                    node_timeout=timeout)

    @steps_checker.step
    def clean_nodes(self, nodes, cleansteps, check=True, timeout=0):
        """Step to clean nodes.

        Args:
            nodes (list): the list of ironic nodes.
            cleansteps (list): Steps for cleaning nodes
            check (bool): flag whether to check step or not.
            timeout (int): seconds to wait a result of state change.

        Raises:
            AssertionError: if clean goes to fail.
        """
        for node in nodes:
            node = self._get_node(node.uuid)
            self._client.node.set_provision_state(node_uuid=node.uuid,
                                                  state='clean',
                                                  cleansteps=cleansteps)
        if check:
            self.check_ironic_nodes_provision_state(nodes=nodes,
                                                    state='clean',
                                                    node_timeout=timeout)

    @steps_checker.step
    def boot_servers(self, nodes):
        """Step to boot ironic nodes.

        #. Set ironic nodes state 'active'
        #. Check ironic nodes state
        #. Get instances IP addresses
        #. Check instances are reachable via IP

        Returns:
            list of objects: ironic nodes
        """
        self.set_nodes_provision_state(nodes, state='active', check=False)

        self.check_ironic_nodes_provision_state(
            nodes,
            state='active',
            node_timeout=config.CHANGE_NODE_STATE_TIMEOUT)

        ip_addresses = self.get_instance_ipv4_addresses(nodes)

        ssh_connection(ipv4_addresses=ip_addresses,
                       username=config.IMAGE_USERNAME,
                       password=config.IMAGE_PASSWORD,
                       timeout=config.SSH_TIMEOUT)

    @steps_checker.step
    def check_ssh_connection(self, nodes):
        """Step to check ssh connection to instance.

        Args:
            nodes (list): the list of ironic nodes.

        Raises:
            AssertionError: if ssh connection wasn't established.
        """
        ip_addresses = self.get_instance_ipv4_addresses(nodes)
        ssh_connection(ipv4_addresses=ip_addresses,
                       username=config.IMAGE_USERNAME,
                       password=config.IMAGE_PASSWORD,
                       timeout=config.SSH_TIMEOUT)

    @steps_checker.step
    def set_nodes_state_bad_request(self, nodes, state):
        """Step to check that bed request is called.

        Args:
            nodes (list): the list of ironic nodes.
            state (string): The desired provision state.

        Raises:
            AssertionError: if particular assert wasn't applied.
        """
        for node in nodes:
            try:
                self._client.node.set_provision_state(node_uuid=node.uuid,
                                                      state=state)
            except exceptions.BadRequest as e:
                node = self._get_node(node.uuid)
                assert_that(e.http_status, equal_to(400))
                assert_that(
                    e.message,
                    matches_regexp(
                        r'The requested action \"{0}\" can not be performed on'
                        r' node \"{1}\" while it is in state \"{2}\".'.format(
                            state, node.uuid, node.provision_state)))

    @steps_checker.step
    def set_nodes_state_bad_request_maintenance(self, nodes, state):
        """Step to check that bad request is called.

        Args:
            nodes (lst): the list of ironic nodes.
            state (string): The desired maintenance state.

        Raises:
            AssertionError: if particular assert wasn't applied.
        """
        for node in nodes:
            try:
                self._client.node.set_provision_state(
                    node_uuid=node.uuid,
                    state=state)
            except exceptions.BadRequest as e:
                node = self._get_node(node.uuid)
                assert_that(e.http_status, equal_to(400))
                assert_that(
                    e.message,
                    matches_regexp(
                        r"The provisioning operation can't be performed on"
                        r" node {} because it's in maintenance mode.".
                        format(node.uuid)))

    @steps_checker.step
    def attach_nodes_to_chassis(self, nodes, chassis, check=True):
        """Step to attach nodes to chassis.

        Args:
            nodes (list): the list of ironic nodes.
            chassis (list): the list of ironic chassis.
            check (bool): flag whether to check step or not.

        Raises:
            AssertionError: if particular nodes weren't applied.
        """
        node_patch = [{
            'op': 'replace',  # Operation: 'add', 'replace', or 'remove'.
            'path': '/chassis_uuid',
            'value': chassis[0].uuid
        }]

        self.update_nodes(nodes=nodes, patch=node_patch)

        if check:
            self.check_nodes_attached_to_chassis(nodes, chassis)

    @steps_checker.step
    def check_nodes_attached_to_chassis(self, nodes, chassis):
        """Step to check that nodes were attached to chassis.

        Args:
            nodes (list): the list of ironic nodes.
            chassis (list): the list of ironic chassis.

        Raises:
            AssertionError: if nodes weren't attached to chassis.
        """
        for node in nodes:
            node = self._get_node(node.uuid)
            assert_that(node.chassis_uuid, equal_to(chassis[0].uuid))

    @steps_checker.step
    def detach_nodes_from_chassis(self, nodes, chassis, check=True):
        """Step to detach nodes from chassis.

        Args:
            nodes (list): the list of ironic nodes.
            chassis (list): the list of ironic chassis.
            check (bool): flag whether to check step or not.

        Raises:
            AssertionError: if particular nodes weren't applied.
        """
        node_patch = [{
            'op': 'remove',  # Operation: 'add', 'replace', or 'remove'.
            'path': '/chassis_uuid',
            'value': chassis[0].uuid
        }]

        self.update_nodes(nodes=nodes, patch=node_patch)

        if check:
            self.check_nodes_not_attached_to_chassis(nodes, chassis)

    @steps_checker.step
    def check_nodes_not_attached_to_chassis(self, nodes, chassis_list):
        """Step to check that nodes were detached from chassis.

        Args:
            nodes (list): the list of ironic nodes.
            chassis_list (list): the list of ironic chassis.

        Raises:
            AssertionError: if nodes weren't attached to chassis.
        """
        for chassis in chassis_list:
            for node in nodes:
                node = self._get_node(node.uuid)
                assert_that(node.chassis_uuid, is_not(chassis.uuid))
