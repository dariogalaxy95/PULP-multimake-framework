# Copyright 2021 Dario Chechi

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import subprocess
import json
import optparse
import os

abs_path = os.path.abspath(os.path.dirname(__file__))

parser = optparse.OptionParser()
parser.add_option("-f", "--file", dest="filename", help="Select a JSON configuration file", metavar="FILE")

options, _ = parser.parse_args()

with open(options.filename, encoding='utf-8') as json_file:
    json_data = json.load(json_file)

process = 'bash ' + json_data['toolchain']
subprocess.run(process, shell=True)

if (json_data['comparison_type'] == 'cores'):
    process = 'python3 ' + abs_path + '/multimake_cores.py -f ' + str(options.filename)
    subprocess.run(process, shell=True)

elif (json_data['comparison_type'] == 'config'):
    process = 'python3 ' + abs_path + '/multimake_config.py -f ' + str(options.filename)
    subprocess.run(process, shell=True)

elif (json_data['comparison_type'] == 'platform'):
    process = 'python3 ' + abs_path + '/multimake_platform.py -f ' + str(options.filename)
    subprocess.run(process, shell=True)