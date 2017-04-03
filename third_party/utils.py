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

import json
import yaml

from hamcrest import assert_that, equal_to  # noqa

from stepler.third_party import ssh
from stepler.third_party import waiter


def load_from_file(filename):
    """Deserialize JSON or YAML from file.

    :param filename: name of the file containing JSON or YAML.
    :returns: a dictionary deserialized from JSON or YAML.
    :raises: ClientException if the file can not be loaded or if its contents
        is not a valid JSON or YAML, or if the file extension is not supported.
    """
    try:
        with open(filename) as f:
            if filename.endswith('.yaml'):
                return yaml.load(f)
            elif filename.endswith('.json'):
                return json.load(f)
            else:
                # The file is neither .json, nor .yaml, raise an exception
                raise Exception.with_traceback(
                    'Cannot process file "%(file)s" - it must have .json or '
                    '.yaml extension.' % {'file': filename})
    except IOError as e:
        raise Exception.with_traceback(
            'Cannot read file "%(file)s" due to '
            'error: %(err)s' % {'err': e, 'file': filename})
    except (ValueError, yaml.YAMLError) as e:
        # json.load raises only ValueError
        raise Exception.with_traceback(
            'File "%(file)s" is invalid due to error: '
            '%(err)s' % {'err': e, 'file': filename})


def ssh_connection(ipv4_addresses,
                   username,
                   password,
                   timeout=0,
                   check=True):
    """Connect to the remote host through SSH.

    Args:
        ipv4_addresses (list): list of ipv4_addresses or hostnames
            of remote hosts
        username (str): username to login
        password (str): password to login

    Returns:
        tuple of objects: (ssh_stdin, ssh_stdout, ssh_stderr)

    Raises:
        RuntimeError: if `server_ssh` is not closed
        TimeoutExpired: if check failed after timeout
    """
    hosts = []
    for ipv4_address in ipv4_addresses:
        host_ssh = ssh.SshClient(host=ipv4_address,
                                 username=username,
                                 password=password,
                                 timeout=timeout)
        hosts.append(host_ssh)

    if check:
        for host in hosts:
            check_ssh_connection_establishment(host, timeout=timeout)


def check_ssh_connection_establishment(server_ssh,
                                       must_work=True,
                                       timeout=0):
    """Step to check that ssh connection can be established.
    Args:
        server_ssh (ssh.SshClient): ssh connection.
        must_work (bool, optional): flag whether 'server_ssh' should be
            able to connect or not.
        timeout (int, optional): seconds to wait a result of check.

    Raises:
        RuntimeError: if `server_ssh` is not closed
        TimeoutExpired: if check failed after timeout
    """
    err_msg = "Invalid SSH connection status to {}".format(server_ssh)
    if timeout:
        err_msg += " during polling time {} second(s)".format(timeout)

    def _check_ssh_connection_establishment():
        return waiter.expect_that(
            server_ssh.check(), equal_to(must_work), err_msg)

    waiter.wait(_check_ssh_connection_establishment,
                timeout_seconds=timeout)
