#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gitea_repo
short_description: Manage repo on user's behalf
description:
  - Manage repo on user's behalf
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
  auto_init:
    decription: Whether the repository should be auto-intialized
  description:
    description: Description of the repository to create
  gitignores:
    decription: Gitignores to use
  issue_labels:
    description: Issue Label set to use
  license:
    description: License to use
  name:
    description: Name of the repository to create
    required: True
  private:
    description: Whether the repository is private
  readme:
    description: Readme of the repository to create
  username:
    description: Username of the user. This user will own the created repository
    required: True
'''

EXAMPLES = '''
'''

import giteapy
from giteapy.rest import ApiException

from ansible.module_utils.aws.core import AnsibleModule
from ..module_utils.helper_functions import _configure_connection


def _create_repo(module, api_instance):
    params = dict(
        auto_init=module.params.get('auto_init'),
        description=module.params.get('description'),
        gitignores=module.params.get('gitignores'),
        issue_labels=module.params.get('issue_labels'),
        license=module.params.get('license'),
        name=module.params.get('name'),
        private=module.params.get('private'),
        readme=module.params.get('readme='),
    )
    params_get = dict(
        owner=module.params.get('username'),
        repo=module.params.get('name'),
    )
    params_conn = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    kwargs = dict((k, v) for k, v in params.items() if v is not None)

    username = module.params.get('username')

    changed = False

    repo_instance = _configure_connection(params_conn, "repo")
    try:
        api_response = repo_instance.repo_get(**params_get)
    except Exception as e:
        exists = False
    else:
        exists = True

    if exists:
        module.exit_json(changed=changed, **api_response.to_dict())
        pass

    repo = giteapy.CreateRepoOption(**kwargs)

    try:
        api_response = api_instance.admin_create_repo(username, repo)
        changed = True
    except ApiException as e:
        module.fail_json(msg="Exception when calling AdminApi->admin_create_repo: %s" % e)
    else:
        module.exit_json(changed=changed, **api_response.to_dict())


def _delete_repo(module, api_instance):
    module.fail_json(msg="Not implemented yet")


def _main():
    argument_spec = dict(
        gitea_host=dict(required=True, default=None),
        gitea_user=dict(required=True, default=None),
        gitea_password=dict(required=True, default=None, no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        username=dict(required=True, default=None),
        auto_init=dict(required=False, default=None, type='bool'),
        description=dict(required=False, default=None),
        gitignores=dict(required=False, default=None),
        issue_labels=dict(required=False, default=None),
        license=dict(required=False, default=None),
        name=dict(required=True, default=None),
        private=dict(required=False, default=None, type='bool'),
        readme=dict(required=False, default=None),
    )

    choice_map = {
        'present': _create_repo,
        'absent': _delete_repo,
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
