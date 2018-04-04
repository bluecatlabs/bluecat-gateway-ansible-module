#!/usr/bin/python
# Copyright 2018 BlueCat Networks (USA) Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By: BlueCat Networks

from ansible.module_utils.basic import AnsibleModule
import requests
import json
import urllib
import re
import os
from collections import OrderedDict

requests.packages.urllib3.disable_warnings()

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'bluecat'
}

DOCUMENTATION = '''
---
module: Bluecat Ansible Module for Gateway

short_description: This is an experimental Ansible module for integrating with Bluecat Integrity Gateway

version_added: "1.0"

description:
    - "Manage Bluecat Integrity Gateway and Bluecat Address Manager via REST API

options:
    username:
        description:
            - Bluecat Address Manager API username
            - The user must be at least an API user and should have permissions to access the resources on Address Manager
        required: true
    password:
        description:
            - Bluecat Address Manager API user password
        required: true
    protocol:
        description:
            - HTTP or HTTPS for connecting to Bluecat Integrity Gateway
        required: false
    domain:
        description:
            - Fully qualified domain name or IP address for Bluecat Integrity Gateway
        required: true
    version:
        description:
            - Version of Bluecat Integrity Gateway REST API to use
        required: true
    resource:
        description:
            - Bluecat Address Manager resource to retrieve
        required: true
    action:
        description:
            - HTTP method to perform, GETALL is used in place of GET for retrieving a collection of resources
        required: true
        choices: ["GET", "PUT", "DELETE", "POST", "GETALL"]
author:
    - Xiao Dong (@xiax)
'''

EXAMPLES = '''
# Get zones in a zone
---
- hosts: localhost
  vars_files:
    - external_vars.yml
  tasks:
  - bluecat:
      username: "{{ username }}"
      password: "{{ password }}"
      protocol: "{{ protocol }}"
      domain: "{{ domain }}"
      version: "{{ version }}"
      resource: zone
      action: getall
      resource_path:
        - zone: "{{ zone }}"
    register: result

# Same as above except parent zones are specified in playbook:
---
- hosts: localhost
  vars_files:
    - external_vars.yml
  tasks:
  - bluecat:
      username: "{{ username }}"
      password: "{{ password }}"
      protocol: "{{ protocol }}"
      domain: "{{ domain }}"
      version: "{{ version }}"
      resource: zone
      action: getall
      resource_path:
        - zone:
          - parent_zone1
          - parent_zone2
    register: result

# external_vars.yml file:
username: portalUser
password: portalUser
protocol: http
domain: localhost
version: 1
'''

RETURN = '''
status_code:
    description: The status code returned by the BAM for the REST API request
    type: int
msg:
    description: The output message that may have been generated as a result of the request
json:
    description: The JSON returned by the request
'''


class Gateway(object):
    def __init__(self, api_json, protocol, domain, version, username, password, mocked=False, **kwargs):
        self.base_url = '{protocol}://{domain}'.format(protocol=protocol, domain=domain)
        self.api_url = self.base_url + '/api/v{version}/'.format(version=version)
        self.username = username
        self.password = password
        if api_json:
            self.json = api_json
        else:
            self.json = self.get_api_json()
        self.session = requests.Session()
        self.mocked = mocked
        # List of one item dictionaries
        self.resource_path = kwargs['resource_path']
        self.json_data = kwargs['json_data']
        self.response_key = {'PUT': 204, 'POST': 201, 'DELETE': 204}

    def get_api_json(self):
        response = requests.get(self.api_url + 'gateway_api.json/')
        with open('gateway_api.json', 'w') as api_json_file:
            api_json_file.write(json.dumps(response.json()))
        return response.json()['resources']

    @staticmethod
    def remove_none_parameters(parameters):
        result_dict = {}
        for key, value in parameters.items():
            if value is not None:
                result_dict[key] = value
        return result_dict

    def login(self, username, password):
        self.session.post('{base_url}/rest_login'.format(base_url=self.base_url),
                          data={'username': username, 'password': password})

    def logout(self):
        self.session.get('{base_url}/logout'.format(base_url=self.base_url))

    def generate_mocked_response(self, resource, action):
        response = requests.models.Response()
        response.status_code = self.response_key[action.upper()]
        response._content = {'message': 'No changes made to {resource}'.format(resource=resource)}
        return response

    def invoke(self, resource, action):
        if self.mocked and action.lower() not in ['get']:
            return self.generate_mocked_response(resource, action)
        resource = resource.lower()
        action = action.lower()
        get_all = False
        if action == 'getall':
            get_all = True
            action = 'get'

        self.login(self.username, self.password)
        definition = self.json[resource][action]
        query_params = {}

        # Populate query_params with any matches in kwargs
        for key, value in definition['query_parameters'].items():
            if key in self.json_data:
                query_params[key] = self.json_data[key]

        # Populate path_params with any matches in kwargs
        resources = OrderedDict()
        for resource in self.resource_path:
            # There should only be one item in each resource defined in resource_path
            for key, value in resource.items():
                resources[key] = value

        # Populate processed_path_params with paths that match user provided path parameters
        processed_path_params = {}
        for path, parameters in definition['path_parameters'].items():
            # Make sure parameters user gave match parameters accepted by path
            if set(parameters.keys()) != set(resources.keys()):
                continue

            processed_path_params[path] = {}
            last_param_position = 0
            for param, value in resources.items():
                # Make sure path parameter order matches order that user specified parameters in
                param_position = path.find('{' + param + '}')
                if last_param_position >= param_position:
                    del processed_path_params[path]
                    break
                else:
                    last_param_position = param_position

                # If value is a list, have to split it into a recursive path
                if isinstance(value, list):
                    search_string = r'/([^/]+)/(\{%s\})' % param
                    match = re.search(search_string, path)
                    if match:
                        value_string = '%s' % value[0]
                        for item in value[1:]:
                            value_string += '/{resource}/{item}'.format(resource=match.group(1), item=item)
                        processed_path_params[path][param] = value_string

                # Escape path parameters to be safe for URLs
                if param not in processed_path_params[path]:
                    try:
                        escaped_value = urllib.quote(value.encode('utf8'))
                    except AttributeError:
                        escaped_value = value
                    processed_path_params[path][param] = escaped_value

        # If more than one path matched user parameters, check which we should use based on get_all flag
        if len(processed_path_params.keys()) > 1 and get_all:
            for path in processed_path_params.keys():
                if path.strip('/').endswith('}'):
                    del processed_path_params[path]
            processed_path_params = OrderedDict(sorted(processed_path_params.items(), key=lambda t: len(t[0]), reverse=True))

        # Insert user provided parameter values into path
        url_path = ''
        for path in processed_path_params:
            try:
                url_path = path.format(**processed_path_params[path])
                break
            except KeyError:
                continue

        if not url_path:
            raise Exception('Provided parameters does not match any valid paths!')

        url_path = url_path.strip('/')
        response = self.session.request(action, self.api_url + url_path + '/', json=query_params)
        self.logout()
        return response


def run_module():
    # param_json = json_data['parameters']

    # Arguments that a user can pass to the module
    module_args = dict(
        protocol=dict(type='str', default='HTTPS', choices=['http', 'https', 'HTTP', 'HTTPS']),
        domain=dict(type='str', required=True),
        version=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        action=dict(type='str', required=True,
                    choices=['GET', 'PUT', 'DELETE', 'POST', 'put', 'delete', 'post', 'get', 'getall', 'GETALL']),
        resource_path=dict(type='list', default=[]),
        json_data=dict(type='dict', default={})
    )

    api_json = {}
    if os.path.isfile('gateway_api.json'):
        json_data = json.load(open('gateway_api.json'))
        api_json = json_data['resources']
        module_args['resource'] = dict(type='str', required=True, choices=api_json.keys())
    else:
        module_args['resource'] = dict(type='str', required=True)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    resource = module.params['resource']
    action = module.params['action']

    if module.check_mode and action.lower() not in ['get', 'getall']:
        gateway = Gateway(api_json, mocked=True, **module.params)
    else:
        gateway = Gateway(api_json, **module.params)

    result = dict(changed=False, msg='')

    try:
        response = gateway.invoke(resource, action)
    except Exception as e:
        gateway.logout()
        raise e
    else:
        if response.status_code in [201, 204] and not module.check_mode:
            result['changed'] = True
        result['status'] = response.status_code
        result['json'] = str(response.content)
        if response.status_code >= 400:
            result['msg'] = 'Bad Status Code'
            module.fail_json(**result)
        module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()