#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gitea_user_info
short_description: Get info existing users 
description:
  - Get info existing users
  - ATM only supports basic auth login
requirements: [ 'giteapy' ]
author:
  - "Kenneth Cummings (kenneth@fliacummings.de)"
extends_documentation_fragment:
  - kenchrcum.gitea.gitea_auth
'''

EXAMPLES = '''
'''

from ansible.module_utils.basic import AnsibleModule
from giteapy.rest import ApiException

from ..module_utils.helper_functions import _configure_connection


def _main():
    argument_spec = dict(
        gitea_host=dict(required=True, default=None),
        gitea_user=dict(required=True, default=None),
        gitea_password=dict(required=True, default=None, no_log=True),
    )

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

    api_instance = _configure_connection(connection_params, "admin")

    users = []
    try:
        api_response = api_instance.admin_get_all_users()
        for entry in api_response:
            user = entry.to_dict()
            users.append(user)
    except ApiException as e:
        module.fail_json(msg="Exception when calling AdminApi->admin_get_all_users: %s" % e)
    else:
        module.exit_json(changed=False, users=users)



if __name__ == '__main__':
    _main()
