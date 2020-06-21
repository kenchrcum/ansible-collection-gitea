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

from ..module_utils.helper_functions import _configure_connection, _delete_nulls, _compare_dict_with_resource


def _create_issue(module, api_instance):
    params = dict(
        assignee=module.params.get('assignee'),
        assignees=module.params.get('assignees'),
        body=module.params.get('body'),
        closed=module.params.get('closed'),
        due_date=module.params.get('due_date'),
        labels=module.params.get('labels'),
        milestone=module.params.get('milestone'),
        title=module.params.get('title'),
    )
    owner = module.params.get('owner')
    repo = module.params.get('repo')

    kwargs = _delete_nulls(params)

    changed = False
    exists = False
    try:
        api_response = api_instance.issue_list_issues(owner=owner, repo=repo)
        for iss in api_response:
            iss = iss.to_dict()
            if iss.get('title') == kwargs.get('title'):
                issue = iss
                issue['assignee'] = iss["assignee"]["login"]
                exists = True
                index = issue['id']
    except ApiException as e:
        module.fail_json(msg="Exception when calling IssueApi->issue_list_issues: %s" % e)

    if exists:
        ### TODO: api_instance.issue_edit_issue() always fails atm. Must be checked, but should work like this
        # compare = _compare_dict_with_resource(kwargs, issue)
        # if compare['change']:
        #     body = giteapy.EditIssueOption(**kwargs)
        #     try:
        #         api_response = api_instance.issue_edit_issue(owner=owner, repo=repo, index=index, body=body)
        #         changed=True
        #     except ApiException as e:
        #         module.fail_json(msg="Exception when calling IssueApi->issue_edit_issue: %s" % e)
        module.exit_json(changed=changed, **issue)

    body = giteapy.CreateIssueOption(**kwargs)

    try:
        api_response = api_instance.issue_create_issue(owner=owner, repo=repo, body=body)
        changed = True
    except ApiException as e:
        module.fail_json(msg="Exception when calling IssueApi->issue_create_issue: %s" % e)
    else:
        module.exit_json(changed=changed, **api_response.to_dict())


def _delete_issue(module, api_instance):
    module.fail_json(msg='not yet implemented')


def _main():
    argument_spec = dict(
        gitea_host=dict(required=True, default=None),
        gitea_user=dict(required=True, default=None),
        gitea_password=dict(required=True, default=None, no_log=True),
        state=dict(default='present', choices=['present', 'absent']),
        owner=dict(required=True, default=None),
        repo=dict(required=True, default=None),
        assignee=dict(required=False, default=None),
        assignees=dict(required=False, default=None, type='list', elements='str'),
        body=dict(required=False, default=None),
        closed=dict(required=False, default=None, type='bool'),
        due_date=dict(required=False, default=None),
        labels=dict(required=False, default=None, type='list', elements='int'),
        milestone=dict(required=False, default=None),
        title=dict(required=True, default=None),
    )

    choice_map = {
        'present': _create_issue,
        'absent': _delete_issue,
    }

    module = AnsibleModule(argument_spec=argument_spec, mutually_exclusive=['assignee', 'assignees'])

    connection_params = dict(
        host=module.params.get('gitea_host'),
        username=module.params.get('gitea_user'),
        password=module.params.get('gitea_password'),
    )

    api_instance = _configure_connection(connection_params, "issue")

    choice_map.get(module.params.get('state'))(module, api_instance)


if __name__ == '__main__':
    _main()
