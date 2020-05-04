from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
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
'''
