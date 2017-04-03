"""
------
Config
------
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

import os

from stepler import config
from third_party.utils import load_from_file

user_data = load_from_file("/home/vagrant/.config/openstack/clouds.yaml")
bifrost_auth = user_data['clouds']['bifrost-admin']['auth']
config.PROJECT_NAME = bifrost_auth['project_name']
config.PASSWORD = bifrost_auth['password']
config.AUTH_URL = bifrost_auth['auth_url']
config.USERNAME = bifrost_auth['username']
config.KEYSTONE_API_VERSION = user_data['clouds']['bifrost']['identity_api_version']  # noqa

# Reports
TEST_REPORTS_DIR = os.environ.get(
    "TEST_REPORTS_DIR",
    os.path.join(os.getcwd(),  # put results to folder where tests are launched
                 "test_reports"))

TEST_REPORTS_DIR = os.path.abspath(os.path.expanduser(TEST_REPORTS_DIR))
if not os.path.exists(TEST_REPORTS_DIR):
    os.mkdir(TEST_REPORTS_DIR)

# Ironic
CURRENT_IRONIC_VERSION = '1'
CURRENT_IRONIC_MICRO_VERSION = '1.30'
CHANGE_NODE_STATE_TIMEOUT = 600
AVAILABLE_NODE_STATE_TIMEOUT = 120
SSH_TIMEOUT = 300
REBOOT_TIMEOUT = 20

# Image credentials
IMAGE_USERNAME = 'cirros'
IMAGE_PASSWORD = 'cubswin:)'

# Ansible image credentials
ANSIBLE_IMAGE_USERNAME = 'ansible'
ANSIBLE_IMAGE_PASSWORD = 'secret'

# Ironic images
NODES_INFO = load_from_file('/home/vagrant/nodes_creds.yaml')
DEPLOY_KERNEL_IMAGE = 'http://10.100.0.2:8080/deploy_kernel'
DEPLOY_RAMDISK_IMAGE = 'http://10.100.0.2:8080/deploy_ramdisk'
BOOT_IMAGE = 'http://10.100.0.2:8080/deployment_image.qcow2'

# Ironic driver
PXE_IPMITOOL_ANSIBLE = 'pxe_ipmitool_ansible'

NODE_PATCH = [{
    'op': 'add',
    'path': '/instance_info/image_source',
    'value': BOOT_IMAGE
}]

# Cleaning nodes
CLEANING_NODES_TIMEOUT = 1200
CLEANSTEPS = [{"interface": "deploy",
               "step": "erase_devices_metadata",
               "args": {"tags": "zap"}}]

# Cleanup
CLEANUP_UNEXPECTED_BEFORE_TEST = bool(
    os.environ.get('CLEANUP_UNEXPECTED_BEFORE_TEST', False))

CLEANUP_UNEXPECTED_AFTER_TEST = bool(
    os.environ.get('CLEANUP_UNEXPECTED_AFTER_TEST', False))

CLEANUP_UNEXPECTED_AFTER_ALL = bool(
    os.environ.get('CLEANUP_UNEXPECTED_AFTER_ALL', False))
