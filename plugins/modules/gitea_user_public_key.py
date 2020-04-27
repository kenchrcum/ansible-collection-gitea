#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gitea_user
short_description: Manage user's public keys
description:
  - Manage user's public keys
  - ATM only supports basic auth login
requirements: [ 'giteapy' ]
author: "Kenneth Cummings (kenneth@fliacummings.de)"
options:
  gitea_host:
    description: URL of the gitea API Endpoint
    required: True
  gitea_user:
    description: gitea login user
    required: True
  gitea_password:
    description: gitea login password
    required: True
  state:
    decription: desired state of the public key
  key:
    decription: ssh public key to add. Required when state=present
  key_id:
    description: id of the key to be deleted. Required when state=absent
  title:
    decription: title of the key. Required when state=present
  username:
    description: of the key owner
    required: True
'''

EXAMPLES = '''
'''

import giteapy
from giteapy.rest import ApiException

from ansible.module_utils.aws.core import AnsibleModule
from ansible_collections.kenchrcum.gitea.plugins.module_utils.helper_functions import _configure_connection, \
    _compare_dict_with_resource


def _create_user_public_key(module, api_instance):
    params = dict(
        key=module.params.get('key'),
        title=module.params.get('title'),
    )
    params_get = dict(
        username=module.params.get('username'),
    )
    params_conn = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    changed = False

    user_instance = _configure_connection(params_conn, "user")

    api_response = user_instance.user_list_keys(**params_get)

    for entry in api_response:
        key = entry.to_dict()
        compare = _compare_dict_with_resource(params, key)
        if not compare["change"]:
            module.exit_json(changed=changed)

    key = giteapy.CreateKeyOption(**kwargs)

    try:
        api_response = api_instance.admin_create_public_key(params_get.get('username'), key=key)
        changed = True
    except ApiException as e:
        if "Key content has been used" in str(e):
            module.fail_json(msg="The key seems to be locked. Probably already in use.")
        elif "Key title has been used" in str(e):
            module.fail_json(msg="Key title has been used. To reuse name, try running state=absent first")
        else:
            module.fail_json(msg="Exception when calling AdminApi->admin_create_public_key: %s" % e)
    else:
        module.exit_json(changed=changed, **api_response.to_dict())


def _delete_user_public_key(module, api_instance):
    params = dict(
        username=module.params.get('username'),
        id=module.params.get('key_id'),
    )

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    changed = False

    try:
        api_instance.admin_delete_user_public_key(**kwargs)
        changed = True
    except ApiException as e:
        if "Reason: Not Found" in str(e):
            module.exit_json(changed=changed)
        else:
            module.fail_json(msg="Exception when calling AdminApi->admin_delete_user_public_key: %s" % e)
    else:
        module.exit_json(changed=changed)


def _main():
    argument_spec = dict(
        gitea_host=dict(required=True, default=None),
        gitea_user=dict(required=True, default=None),
        gitea_password=dict(required=True, default=None, no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        username=dict(required=True, default=None),
        key=dict(required=False, default=None),
        title=dict(required=False, default=None),
        key_id=dict(required=False, default=None, type='int'),
    )
    choice_map = {
        'present': _create_user_public_key,
        'absent': _delete_user_public_key,
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['key', 'title']),
            ('state', 'absent', ['key_id']),
        ]
    )

    connection_params = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    api_instance = _configure_connection(connection_params, "admin")

    choice_map.get(module.params.get('state'))(module, api_instance)


if __name__ == '__main__':
    _main()
