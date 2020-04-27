import giteapy


def _compare_dict_with_resource(input, resource):
    change = False
    updated_keys = []
    for k, v in input.items():
        if str(resource[k]) != str(v):
            change = True
            updated_keys.append(k)
    if change:
        return dict(change=change, updated_keys=updated_keys)
    else:
        return dict(change=change)


def _connect_to_gitea(connection_params):
    configuration = giteapy.Configuration()
    configuration.host = connection_params.get('host')
    configuration.username = connection_params.get('username')
    configuration.password = connection_params.get('password')
    api_instance = giteapy.AdminApi(giteapy.ApiClient(configuration))
    return api_instance
