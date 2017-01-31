.. spaced-armour-tests documentation master file, created by
   sphinx-quickstart on Tue Jan 31 15:10:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
======================================================
Spaced-armour-tests: test ironic_underlay step by step
======================================================

----------
Annotation
----------

Spaced-armour-tests is intended to provide the community with a testing toolkit based on
Stepler framework that is capable of perform testing of ironic_underlay

------------
Architecture
------------

Architecture has following abstraction levels, where code lives (from higher to less):

* **clients** are able to manipulate resources: *users, roles, servers, nodes etc*. For ex: *keystone client, ironic client, etc*.
* **steps** are actions, that we want to make over resources via **clients**: *create, delete, update, etc*. They should end with check, that step was finished correct.
* **fixtures** manage resources *construction, destruction, etc* via **steps**.
* **tests** combine **steps** and **fixtures** according to scenario.

Detailed information about auto tests construction is available in `our guideline <http://autotests-guideline.readthedocs.io/>`_.

Sometimes it needs to have code for *ssh connection, proxy server, etc*. They are not related with **clients**, **steps**, **fixtures** and **tests** and are considered as third party helpers and must be implemented based on its purpose with OOP and design principles.

Spaced-armour-tests uses `py.test <http://doc.pytest.org/>`_ as test runner and `tox <https://tox.readthedocs.io/>`_ for routine operations. Be sure you know them.

--------------
How to install
--------------

Make following commands in terminal::

   git clone https://github.com/Mirantis/spaced-armour-tests.git
   cd spaced-armour-tests
   virtualenv .venv
   . .venv/bin/activate
   pip install -U pip
   pip install -r requirements.txt

----------------
How to run tests
----------------

*If you know how to launch tests with py.test, you may skip this section.*

Before launching you should export some openstack environment variables:

* ``OS_PROJECT_NAME`` (default value ``'baremetal'``)
* ``OS_PASSWORD`` (default value ``'ChangeThisPa55w0rd'``)
* ``OS_AUTH_URL`` (keystone auth url should be defined explicitly: v3 - http://keystone/url/v3)
* ``OS_USERNAME`` (default value ``'bifrost_user'``)


To get details look into ``spaced-armour-tests/config.py``

Let's view typical commands to launch test in different ways:

* If you want to launch all tests (``-v`` is used to show full name and status of each test)::

   py.test spaced-armour-tests -v

* For ex, you write the test ``test_node_create`` and want to launch it only::

   py.test spaced-armour-tests -k test_node_create

* If your test was failed and you want to debug it, you should disable stdout capture::

   py.test spaced-armour-tests -k test_node_create -s

* Full information about ``py.test`` is obtainable with::

   py.test -h

------------------
How to debug tests
------------------

We recommend to use ``ipdb`` to set up break points inside code. Just put following chunk before code line where you want to debug (don't forget about ``-s`` to disable  ``py.test`` stdout capture):

.. code:: python

   import ipdb; ipdb.set_trace()

-----------------
Deep to structure
-----------------

.. toctree::
   :maxdepth: 1

   ironic_underlay
