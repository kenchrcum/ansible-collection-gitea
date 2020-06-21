#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gitea_admin_organization
short_description: Manage gitea organization 
description:
  - Create a gitea organization
  - ATM only supports basic auth login
requirements: [ 'giteapy' ]
author:
  - "Kenneth Cummings (kenneth@fliacummings.de)"
extends_documentation_fragment:
  - kenchrcum.gitea.gitea_auth
options:
  state:
    description: desired state of the organization
  description:
    description: organization description
  full_name:
    description: organization full name
  location:
    description: organization location
  owner:
    description: existing user as owner of the organization
    required: True
  repo_admin_change_team_access:
    description: whether repo admins can change team access
  username:
    description: short name for the organization
    required: True
  visibility:
    description: visibility of the organization
    choices: ['public', 'limited', 'private']
  website:
    description: organization website
'''

EXAMPLES = '''
'''

import giteapy
from ansible.module_utils.basic import AnsibleModule
from giteapy.rest import ApiException

from ..module_utils.helper_functions import _configure_connection, _delete_nulls


def _create_org(module, api_instance):
    params = dict(
        description=module.params.get('description'),
        full_name=module.params.get('full_name'),
        location=module.params.get('location'),
        repo_admin_change_team_access=module.params.get('repo_admin_change_team_access'),
        username=module.params.get('username'),
        visibility=module.params.get('visibility'),
        website=module.params.get('website'),
    )

    kwargs = _delete_nulls(params)

    username = module.params.get('owner')

    changed = False

    api_response = api_instance.admin_get_all_orgs()

    for entry in api_response:
        org = entry.to_dict()
        if org.get('username') == kwargs.get('username'):
            module.exit_json(changed=changed, **org)

    new_org = giteapy.CreateOrgOption(**kwargs)

    try:
        api_response = api_instance.admin_create_org(username, new_org)
        changed = True
    except ApiException as e:
        module.fail_json(msg="Exception when calling AdminApi->admin_create_org: %s" % e)
    else:
        module.exit_json(changed=changed, **api_response.to_dict())


def _delete_org(module, api_instance):
    module.fail_json(msg="Not implemented yet")


def _main():
    argument_spec = dict(
        gitea_host=dict(required=True, default=None),
        gitea_user=dict(required=True, default=None),
        gitea_password=dict(required=True, default=None, no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        owner=dict(required=True, default=None),
        description=dict(required=False, default=None),
        full_name=dict(required=False, default=None),
        location=dict(required=False, default=None),
        repo_admin_change_team_access=dict(required=False, default=None, type='bool'),
        username=dict(required=True),
        visibility=dict(default='public', choices=['public', 'limited', 'private']),
        website=dict(required=False, default=None),
    )

    choice_map = {
        'present': _create_org,
        'absent': _delete_org,
    }

    module = AnsibleModule(argument_spec=argument_spec)

    connection_params = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    api_instance = _configure_connection(connection_params, "admin")

    choice_map.get(module.params.get('state'))(module, api_instance)


if __name__ == '__main__':
    _main()
