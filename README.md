![alt text](bluecat_certified.png "bluecat_certified")

## BlueCat Gateway Module and Playbooks for Ansible

## Dependencies

* Requires BlueCat Gateway v18.10.1 or greater

* You must install the Python "requests" module.

```
pip install requests
```

## Using the module

#### Attention: __You _must_ be familiar with Ansible in order to use the module and playbooks.__

To obtain the BlueCat Ansible module and playbooks, pull or clone this repository.
* `bluecat.py` is the Ansible module
* playbooks are in the Examples folder in YAML format

The first time you run the BlueCat Gateway Module for Ansible, it will download the `gateway_api.json` file from your BlueCat Gateway instance into the same folder where the Ansible playbook was executed.
The module reads from the `gateway_api.json` file to determine what REST API requests your BlueCat Gateway instance supports.
If you upgrade your BlueCat Gateway image or want to connect to a different BlueCat Gateway instance, delete the `gateway_api.json` file in the same folder as the Ansible playbook.

BlueCat recommends that you should not often change variables in `external_vars.yml.` The variables should be set once, and then used with multiple playbooks.

To allow the Ansible playbook to consume the REST APIs within a workflow to call BlueCat Gateway and BlueCat Address Manager (BAM), you must import the REST API workflow into your BlueCat Gateway instance. You can either manually download the REST API workflow from GitHub (https://github.com/bluecatlabs/gateway-workflows/tree/master/Community), or perform a GitHub Import from Workflow Export/Import in the BlueCat Gateway UI (The REST API workflow is imported along with all Examples and Community workflows). Once the REST API workflow is imported, you must set permissions for it using Workflow Permissions, and then you can begin using the workflows.
To view the swagger docs for the REST API go to `<BlueCatGatewayFQDN>/api/v1/`.

## Adhering to standards
When contributing to the BlueCat Gateway Ansible Module, ensure that your code:
- Follows the PEP8 standard
- Uses meaningful variable and function names

## Contributing

1. Fork it!
2. Create your feature branch. `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request.

## License

Copyright 2018 BlueCat Networks, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
