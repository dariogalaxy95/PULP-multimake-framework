# PULP-multimake-framework
This project allows to launch multiple configuration simulations of programs for the PULP platform and compare the results in an easy way.

## Prerequisites

This framwork requires several Python3 libraries.
To obtain them, use the following command:

`$ sudo python3 -m pip install matplotlib numpy regex`

## Input

The input is given by a JSON file as the following:

`{"configuration_name":"Kernel type: Convolution, precision: 888",
    "makefile_path":"/home/dariolinux/Desktop/Tesi/pulp-nn/mixed/XpulpV2/32bit/test",
    "platform_path":"/home/dariolinux/Desktop/Tesi/pulp-sdk/configs/", 
    "platform":"pulp-open.sh",
    "toolchain":"/home/dariolinux/Desktop/Tesi/v1.0.16-pulp-riscv-gcc-ubuntu-18/sourceme.sh", 
    "comparison_type":"cores",
    "compilation_parameters":["perf=1 cores=1 kernel=888", "perf=1 cores=2 kernel=888", "perf=1 cores=4 kernel=888", "perf=1 cores=8 kernel=888"], 
    "freq":450,
    "active_en":12,
    "idle_en":2,
    "uncore_en":8, 
    "operation_name":"MACs"
}`

The elements of the JSON are the following:

-	configuration_name: configuration name, used as title
-	makefile_path: directory where to recall make for compiling
-	platform: path of virtual platform file(s)
-	toolchain: path of toolchain configuration file
-	comparison_type: type of the comparison we want to perform (cores/config/platform)
-	compilation_parameters: compilation parameters to give to make, separated with commas between configurations
-	freq: clock frequency in MHz
-	active_en: active energy in pJ
-	idle_en: idle energy in pJ
-	uncore_en: uncore energy in pJ
-	operation_name: name of operation to perform (ex. MAC).

## Output

To functionally use the framework, the program output must be something like this:

`[0] : num_cycles: 79923
[1] : num_cycles: 79923
[1] : num_instr_miss: 143
[0] : num_instr_miss: 143
[1] : num_ext_load: 1
[0] : num_ext_load: 1
[0] : num_ext_Store: 1
[1] : num_ext_Store: 1
[0] : num_tcdm_contentions: 460
[1] : num_tcdm_contentions: 448
[0] : num_instrs: 70526
[1] : num_instrs: 70526
[0] : num_active_cycles: 79697
[1] : num_active_cycles: 79713
[0] : num_load_stalls: 1993
[1] : num_load_stalls: 1993
[0] : num_jumpr_stalls: 0
[1] : num_jumpr_stalls: 0
[1] : num_branch: 2963
[0] : num_branch: 2963`

where the number in square brackets represents the core ID.

## Usage

To use the framework, browse to the folder where you have downloaded the files and use the following command:

`$ python3 multimake_manager.py -f file.json`

where file.json is the JSON file defined by the user and described in the input paragraph.
