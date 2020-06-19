#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
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
        username=module.params.get('full_name'),
        visibility=module.params.get('visibility'),
        website=module.params.get('website'),
    )
    params_conn = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    kwargs = _delete_nulls(params)

    username = module.params.get('username')

    changed = False

    api_response = api_instance.admin_get_all_orgs()

    for entry in api_response:
        org = entry.to_dict()
        if org.get('full_name') == kwargs.get('full_name'):
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
        username=dict(required=True, default=None),
        description=dict(required=False, default=None),
        full_name=dict(required=True),
        location=dict(required=False, default=None),
        repo_admin_change_team_access=dict(required=False, default=None, type='bool'),
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
