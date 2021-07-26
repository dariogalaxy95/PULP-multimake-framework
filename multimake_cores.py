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
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re
import json
import optparse

def GetNumbers(string):  # extracts numbers from a string
    array = re.findall(r'[0-9]+', string)
    return array

def GetSpeedup(seq, par):  # calculates the speedup as ratio between number of cycles in sequential case and in parallel case
    r = float(seq/par)
    return round(r,2)

def GetCores(config):  # extracts the number of cores from a string
    s = re.findall(r'\[\d+\]', config)
    s = ''.join(s)
    s = re.findall(r'\d+', s)
    ints = [int(item) for item in s]
    m = max(ints)+1
    print('Number of cores: ' + str(m) + '\n\n')
    return m

def InitDict(dictionary, n_cores):  # initializes the dictionary
    for key in dictionary:
        if (key != 'op') and (key != 'errors'):
            dictionary[key] = [0]*n_cores

def GetMean(val_list):  # calculates the mean value of a list of values
    result = 0
    for i in range(len(val_list)):
        result += val_list[i]
    result = result/len(val_list)
    return int(result)

def MeanPowerConsumption(freq, active_en, idle_en, uncore_en, conf_num):  # calculates the power consumption (mean of the single cores)
    total_en = 0
    for i in range(num_cores[conf_num]):
        total_en += active_en * resultlist[conf_num]['num_active_cycles'][i]
        total_en += idle_en * (resultlist[conf_num]['num_cycles'][i] - resultlist[conf_num]['num_active_cycles'][i])
    total_en += uncore_en * resultlist[conf_num]['num_cycles'][0]
    total_en *= 10**(-9)
    total_en = total_en / (resultlist[conf_num]['num_cycles'][0] * (10**-6) / freq)
    return round(total_en, 2)

def GetOverhead(conf_num):  # calculates the overhead
    tmp_list = []
    for i in range(num_cores[conf_num]):
        tmp_list.append(resultlist[conf_num]['num_instrs'][i])
    exec_stage = GetMean(tmp_list)
    tmp_list = []
    for i in range(num_cores[conf_num]):
        tot_ovh = resultlist[conf_num]['num_active_cycles'][i] - resultlist[conf_num]['num_instrs'][i]
        tmp_list.append(tot_ovh - resultlist[conf_num]['num_tcdm_contentions'][i] - resultlist[conf_num]['num_load_stalls'][i])
    other_overhead = GetMean(tmp_list)
    return [exec_stage, other_overhead]

def GetPercentage(val_list):  # calculates the percentages to be used in the pie chart
    total = 0
    perc = []
    for elem in val_list:
        total += elem
    for elem in val_list:
        perc.append(round((elem/total) * 100,1))
    return perc

def GetSize(number):  # returns the size of a matrix which can contain the number passed
    r = 0
    c = 0
    while ((r*c) < number):
        if (r<c):
            r += 1
        else:
            c += 1
    return [r,c]



parser = optparse.OptionParser()
parser.add_option("-f", "--file", dest="filename", help="Select a JSON configuration file", metavar="FILE")

options, _ = parser.parse_args()

with open(options.filename, encoding='utf-8') as json_file:
    json_data = json.load(json_file)

# Extracting settings from JSON file
configuration_name = json_data['configuration_name']
makefile_path = json_data['makefile_path']
compilation_parameters = json_data['compilation_parameters']
platform_path = json_data['platform_path']
opname = json_data['operation_name']

resultlist = []
num_cores = []

if (platform_path.endswith('/') == False): 
    platform_path += '/'

source_cmd = 'source ' + json_data['toolchain'] + ' && source ' + platform_path + json_data['platform'] # configuration of toolchain and virtual platform


for conf_num in range(len(compilation_parameters)):

    make_string = source_cmd + ' && make clean all ' + compilation_parameters[conf_num]
    if (compilation_parameters[conf_num] != ""):
        print('Configuration ' + str(conf_num+1) + ': ' + compilation_parameters[conf_num] + '\n')
    else:
        print('Configuration ' + str(conf_num+1) + ': ' + 'no parameters' + '\n')
    
    process = subprocess.run(make_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=makefile_path, executable='/bin/bash')
    make_string = source_cmd + ' && make run -s'
    process = subprocess.run(make_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=makefile_path, encoding='UTF-8', executable='/bin/bash')

    print(process.stdout)

    # Obtain number of cores of this configuration

    num_cores.append(GetCores(process.stdout))

    # Initialization of result dictionary

    results = {'op':0, 'num_cycles':[], 'num_instr_miss':[], 'num_ext_load':[], 'num_ext_Store':[], 'num_tcdm_contentions':[], 'num_instrs':[], 'num_active_cycles':[], 'num_load_stalls':[], 'num_jumpr_stalls':[], 'num_branch':[], 'errors':0}

    InitDict(results, num_cores[conf_num])

    # Preparation of results
    
    if (opname != ""):
        spt = re.findall( opname+'=\d+', str(process.stdout))
        tmp = re.split('=', spt[0])
        results['op'] = int(tmp[1])


    for key in results:
        if (key != 'op') and (key != 'errors'):
            spt = re.findall(r'\[\d+\] : ' + key + ': \d+', process.stdout)
            if spt: # list not empty
                for i in range(len(spt)):
                    tmp = re.split(':', spt[i])
                    results[key][i] = int(tmp[2])


    # Results ready, they are inserted in the results list
    resultlist.append(results)


# Calculation of the speedup
spdup = []
for core_id in range(len(num_cores)): 
    if (num_cores[core_id] == 1):  # checking what configuration is the sequential one (1 core) -> now i have core_id
        break

# Now I know what configuration is the sequential one and I can calculate the speedup

for i in range(len(resultlist)):
    if (i != core_id):
        spdup.append(GetSpeedup(GetMean(resultlist[core_id]['num_cycles']), GetMean(resultlist[i]['num_cycles'])))

# Calculation of power consumption
pwr_cons = []
for i in range(len(resultlist)):
    pwr_cons.append(MeanPowerConsumption(json_data['freq'], json_data['active_en'], json_data['idle_en'], json_data['uncore_en'], i))

# Calculation of op/cycle
if (opname != ""):
    op_cycle = []
    for i in range(len(resultlist)):
        op_cycle.append(round(resultlist[i]['op']/resultlist[i]['num_cycles'][0], 3))


# Calculation of overheads
ovh = []
for i in range(len(resultlist)):
    tmp_list = GetOverhead(i)
    tmp_list.append(GetMean(resultlist[i]['num_load_stalls']))
    tmp_list.append(GetMean(resultlist[i]['num_tcdm_contentions']))
    ovh.append(tmp_list)


perc = []
for i in range(len(resultlist)):
    perc.append(GetPercentage(ovh[i]))


# Creation of the graph plots

if (opname != ""):
    fig, (ax_cycles, ax_speedup, ax_opcycles, ax_pwr) = plt.subplots(1, 4, figsize=(12,7))
else:
    fig, (ax_cycles, ax_speedup, ax_pwr) = plt.subplots(1, 3, figsize=(12,7))

# ---------------------------  Cycles plot  ----------------------------------------------

rects = []
rects_active = []
values = []
values_active = []
conf_name = []

for i in range(len(resultlist)):
    if (num_cores[i] == 1):
        conf_name.append('1 Core')
    else:
        conf_name.append(str(num_cores[i]) + ' Cores')

    values.append(GetMean(resultlist[i]['num_cycles']))
    values_active.append(GetMean(resultlist[i]['num_active_cycles']))


x = np.arange(len(conf_name))  # the label locations
width = 0.35  # the width of the bars

rects = ax_cycles.bar(x - width/2, values, width, label='Total', color='orange')
rects_active = ax_cycles.bar(x + width/2, values_active, width, label='Active', color='red')

# Add some text for labels, title and custom x-axis tick labels, etc.

ax_cycles.set_title('Cycles\n(lower is better)')

ax_cycles.set_xticks(x)
ax_cycles.set_xticklabels(conf_name)

ax_cycles.legend()

#ax_cycles.bar_label(rects, padding=1)
#ax_cycles.bar_label(rects_active, padding=1)

#fig.tight_layout()


# ---------------------------  Speedup plot  ----------------------------------------------

rects = []
values = []
conf_spdup = []
k = 0 
for i in range(len(num_cores)):
    if (i != core_id):
        lbl = str(num_cores[i]) + ' Cores'
        values.append(spdup[k])
        conf_spdup.append(conf_name[i])
        k += 1
        
x = np.arange(len(conf_spdup))
rects = ax_speedup.bar(x, values, width, color='green')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax_speedup.set_title('Speedup\n(higher is better)')

ax_speedup.set_xticks(x)
ax_speedup.set_xticklabels(conf_spdup)


ax_speedup.bar_label(rects, padding=1)

# ---------------------------  Op/cycle plot  ----------------------------------------------

if (opname != ""):
    rects = []
    values = []

    for i in range(len(resultlist)):
        values.append(op_cycle[i])


    x = np.arange(len(conf_name))  # the label locations
    #width = 0.35  # the width of the bars

    rects = ax_opcycles.bar(x, values, width, color='blue')

    # Add some text for labels, title and custom x-axis tick labels, etc.

    ax_opcycles.set_title(json_data['operation_name'] + '/cycle\n(higher is better)')

    ax_opcycles.set_xticks(x)
    ax_opcycles.set_xticklabels(conf_name)

    ax_opcycles.bar_label(rects, padding=1)
            

    fig.tight_layout(rect=[0, 0.03, 1, 0.90])
    fig.suptitle(configuration_name, fontsize=16)

# ---------------------------  Power Consumption plot  ----------------------------------------------

rects = []
values = []

for i in range(len(resultlist)):
    values.append(pwr_cons[i])


x = np.arange(len(conf_name))  # the label locations
#width = 0.35  # the width of the bars

rects = ax_pwr.bar(x, values, width, color='purple')

# Add some text for labels, title and custom x-axis tick labels, etc.

ax_pwr.set_title('Power Consumption (mW)\n(lower is better)')

ax_pwr.set_xticks(x)
ax_pwr.set_xticklabels(conf_name)

ax_pwr.bar_label(rects, padding=1)
        

fig.tight_layout(rect=[0, 0.03, 1, 0.90])
fig.suptitle(configuration_name, fontsize=16)

# ---------------------------  Overhead plot  ----------------------------------------------

label_tmp = ['Execution stage, ', 'Others, ', 'LD stalls, ', 'TCDM contentions, ']

labels = []
percentage = []
for k in range(len(ovh)):
    lbl_tmp = []
    perc_temp = []
    for i in range(len(ovh[k])):
        if (perc[k][i] != 0):  # excluding zero values for overlapping reasons
            lbl_tmp.append(label_tmp[i] + str(ovh[k][i]))
            perc_temp.append(perc[k][i])
    labels.append(lbl_tmp)
    percentage.append(perc_temp)

ax_ovh = []
fig_2 = plt.figure(figsize=(12,8))


size = GetSize(len(ovh))

for i in range(len(ovh)):
    ax_ovh.append(plt.subplot( size[0], size[1], i+1))
    ax_ovh[i].pie(percentage[i], labels=labels[i], shadow=True, autopct='%1.1f%%')
    ax_ovh[i].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    if (i == core_id):
        ax_ovh[i].set_title('1 Core')
    else:
        ax_ovh[i].set_title(str(num_cores[i]) + ' Cores')

plt.show()
