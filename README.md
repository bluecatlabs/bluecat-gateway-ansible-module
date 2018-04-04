# Ansible Bluecat Integrity Gateway Module

Bluecat Integrity Gateway Module for Ansible.

## Dependencies

Python "requests" module

```
pip install requests
```

## Using the module

The first time the module is run it will download the gateway_api.json file from your Gateway instance into the same folder where the ansible playbook was executed.
The module reads from the gateway_api.json file to determine what REST API requests your Gateway instance supports.
If you upgrade your Gateway image or want to connect to a different Gateway instance, please delete the gateway_api.json file in the same folder as the ansible playbook.

## Upgrading the Gateway

When you update your Gateway, please delete the gateway_api.json file found in the same folder as your ansible playbook for communicating with the Gateway.

## Standards
When contributing to the Gateway Ansible Module, please ensure that the code is of good quality
- The Gateway Ansible Module is written with the PEP8 standard in mind
- Use meaningfull variable and function names

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## License

Copyright 2017 BlueCat Networks, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.