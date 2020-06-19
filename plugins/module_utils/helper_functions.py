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


def _configure_connection(connection_params, api):
    configuration = giteapy.Configuration()
    configuration.host = connection_params.get('host')
    configuration.username = connection_params.get('username')
    configuration.password = connection_params.get('password')
    if api == "admin":
        api_instance = giteapy.AdminApi(giteapy.ApiClient(configuration))
    elif api == "issue":
        api_instance = giteapy.IssueApi(giteapy.ApiClient(configuration))
    elif api == "misc":
        api_instance = giteapy.MiscellaneousApi(giteapy.ApiClient(configuration))
    elif api == "org":
        api_instance = giteapy.OrganizationApi(giteapy.ApiClient(configuration))
    elif api == "repo":
        api_instance = giteapy.RepositoryApi(giteapy.ApiClient(configuration))
    elif api == "user":
        api_instance = giteapy.UserApi(giteapy.ApiClient(configuration))
    else:
        raise BaseException("no valid api")
    return api_instance


def _delete_nulls(h):
    """ Remove null entries from a hash
    Returns:
        a hash without nulls
    """
    if isinstance(h, list):
        return [delete_nulls(i) for i in h]
    if isinstance(h, dict):
        return dict((k, delete_nulls(v)) for k, v in h.items() if v is not None)

    return h
