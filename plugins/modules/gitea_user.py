#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gitea_user
short_description: Manage an user in Gitea
description:
  - Manage an user in Gitea
requirements: [ 'giteapy' ]
author: "Kenneth Cummings (kenneth@fliacummings.de)"
options:
'''

EXAMPLES = '''
'''

import giteapy
from giteapy.rest import ApiException

from ansible.module_utils.aws.core import AnsibleModule
from ansible_collections.kenchrcum.gitea.plugins.module_utils.helper_functions import _connect_to_gitea


def _admin_create_user(module, api_instance):
    params = dict(
        email=module.params.get('email'),
        full_name=module.params.get('full_name'),
        login_name=module.params.get('login_name'),
        must_change_password=module.params.get('must_change_pw'),
        password=module.params.get('password'),
        send_notify=module.params.get('send_notify'),
        source_id=module.params.get('source_id'),
        username=module.params.get('username'),
    )

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    changed = False

    api_response = api_instance.admin_get_all_users()

    for entry in api_response:
        user = entry.to_dict()
        if user.get('login') == kwargs.get('username'):
            module.exit_json(changed=changed)

    body = giteapy.CreateUserOption(**kwargs)

    try:
        api_response = api_instance.admin_create_user(body=body)
        changed = True
    except ApiException as e:
        module.fail_json(msg="Exception when calling AdminApi->admin_create_user: %s\n" % e)
    else:
        module.exit_json(changed=changed, **api_response.to_dict())


def _delete_user(module, api_instance):
    params = dict(
        username=module.params.get('username'),
    )

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    changed = False
    exists = False

    api_response = api_instance.admin_get_all_users()

    for entry in api_response:
        user = entry.to_dict()
        if user.get('login') == kwargs.get('username'):
            exists=True

    if exists:
        try:
            api_instance.admin_delete_user(kwargs.get('username'))
            changed = True
        except ApiException as e:
            module.fail_json(msg="Exception when calling AdminApi->admin_delete_user: %s\n" % e)
        else:
            module.exit_json(changed=changed)
    else:
        module.exit_json(changed=changed)


def _main():
    argument_spec = dict(
        gitea_host=dict(required=False, default=None),
        gitea_user=dict(required=False, default=None),
        gitea_password=dict(required=False, default=None, no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        email=dict(required=False, default=None),
        full_name=dict(required=False, default=None),
        login_name=dict(required=False, default=None),
        must_change_pw=dict(required=False, default=None, type='bool'),
        password=dict(required=False, default=None, no_log=True),
        send_notify=dict(required=False, default=None, type='bool'),
        source_id=dict(required=False, default=None, type='int'),
        username=dict(required=True, default=None),
    )

    choice_map = {
        'present': _admin_create_user,
        'absent': _delete_user,
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[
            ('state', 'present', ['email', 'password']),
        ]
    )

    connection_params = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    try:
        api_instance = _connect_to_gitea(connection_params)
    except:
        module.fail_json(msg="could not connect to gitea api")

    choice_map.get(module.params.get('state'))(module, api_instance)


if __name__ == '__main__':
    _main()
