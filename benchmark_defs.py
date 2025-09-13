import os
import re
import glob
from dataclasses import dataclass
import yaml
from typing import Dict, Any, List, Optional, Union 
import pandas as pd

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)


@dataclass
class SingleBenchmarkTask:
    task_name: str
    input_file: str
    data_model: int
    property_file: str
    expected: bool

@dataclass
class SingleBenchmarkResult:
    task: SingleBenchmarkTask
    exit_code: int
    last_line: str
    compile_time: float
    sat_time: float
    processing_time: float
    total_runtime: float
    sat_calls: int

@dataclass
class BenchmarkSet:
    task_name: str
    set_file: str
    property_file: str

@dataclass
class BenchmarkTask:
    input_file: str
    data_model: int
    property_files: Dict[str, str] = None
    task_name: str = None


def parse_yml_file(yml_file: str, single_property: str = None) -> BenchmarkTask:

    base_dir = os.path.dirname(yml_file)
    base_dir_prop = os.path.dirname(base_dir)

    with open(yml_file, 'r') as file:
        data = yaml.safe_load(file)

    task = BenchmarkTask(input_file='', data_model=32, property_files={})

    if 'input_files' in data:
        input_file = os.path.join(base_dir, data['input_files'])
        clean_input_file = input_file.split('sv-benchmarks')[-1][1:] if 'sv-benchmarks' in input_file else input_file
        task.input_file = clean_input_file

    if 'options' in data and 'data_model' in data['options']:
        data_model = data['options']['data_model']
        if 'ILP32' in data_model:
            task.data_model = 32
        elif 'ILP64' in data_model or 'LP64' in data_model:
            task.data_model = 64

    # Extract property files with expected results
    if 'properties' in data:
        property_files: Dict[str, str] = {}
        for prop in data['properties']:
            if 'property_file' in prop and 'expected_verdict' in prop:
                property_relative_path = prop['property_file'][3:]  # Remove the leading '../'
                if single_property and property_relative_path != single_property[2:]: # Remove the leading 'c/'
                    #print(f"{prop['property_file']} vs {single_property}.")
                    continue
                property_file = os.path.join(base_dir_prop, property_relative_path)
                clean_property_file = property_file.split('sv-benchmarks')[-1][1:] if 'sv-benchmarks' in property_file else property_file
                property_files[clean_property_file] = prop['expected_verdict']
        if property_files:
            task.property_files = property_files

    return task

def parse_benchmark_set(benchmark_set: BenchmarkSet, single_property: bool = True) -> List[BenchmarkTask]:

    set_file = config['BASE_DIR'] + "/benchmark/sv-benchmarks/" + benchmark_set.set_file
    tasks: List[BenchmarkTask] = []
    base_dir = os.path.dirname(set_file)

    if not os.path.exists(set_file):
        return tasks  # Return empty list if the set file does not exist
    
    single_property_file = None
    if single_property:
        single_property_file = benchmark_set.property_file
    
    with open(set_file, 'r') as file:
        lines = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]

    for line in lines:
        # Handle wildcards in file paths
        if line.startswith('#'):
            continue
        if '*' in line:
            pattern = os.path.join(base_dir, line)
            matching_files = glob.glob(pattern)
            for yml_file in matching_files:
                parsed_data = parse_yml_file(yml_file, single_property_file)
                parsed_data.task_name = benchmark_set.task_name
                tasks.append(parsed_data)
        else:
            # Handle direct file paths
            yml_file = os.path.join(base_dir, line)
            parsed_data = parse_yml_file(yml_file, single_property_file)
            parsed_data.task_name = benchmark_set.task_name
            tasks.append(parsed_data)

    return tasks

def extract_benchmark_set(benchmark_xml_path: str) -> List[BenchmarkSet]:

    with open(benchmark_xml_path, 'r') as file:
        benchmark_xml = file.read()

    sets: List[BenchmarkSet] = []

    pattern = r'<tasks name="([^"]*)">\s*<includesfile>(.*?)</includesfile>\s*<propertyfile>(.*?)</propertyfile>\s*</tasks>'
    matches = re.findall(pattern, benchmark_xml, re.DOTALL)

    for task_name, set_file, prop_file in matches:
        clean_set_file = set_file.split('sv-benchmarks')[-1][1:] if 'sv-benchmarks' in set_file else set_file
        clean_prop_file = prop_file.split('sv-benchmarks')[-1][1:] if 'sv-benchmarks' in prop_file else prop_file

        sets.append(BenchmarkSet(
            task_name=task_name,
            set_file=clean_set_file,
            property_file=clean_prop_file
        ))

    return sets

LINE_RE = re.compile(
    r'^(?P<inputfile>\S+)\s+(?P<status>.+?)\s+(?P<cpu_time>\d+(?:\.\d+)?)\s+(?P<wall_time>\d+(?:\.\d+)?)\s+(?P<host>\S+)\s*$'
)

def parse_results_txt(txt_path: str) -> pd.DataFrame:
    rows = []
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line or line.startswith('//') or set(line.strip()) == {'-'}:
                continue
            m = LINE_RE.match(line)
            if not m:
                # skip header lines like "inputfile  status  cpu time ..." etc.
                continue
            data = m.groupdict()
            # normalize numeric types
            data['cpu_time'] = float(data['cpu_time'])
            data['wall_time'] = float(data['wall_time'])
            # trim whitespace in status
            data['status'] = data['status'].strip()
            rows.append(data)
    df = pd.DataFrame(rows, columns=['inputfile', 'status', 'cpu_time', 'wall_time', 'host'])
    return df

if __name__ == "__main__":
    df_truefalse = pd.read_csv('./tasks/2ls_truefalse_results.csv')
    df_truefalse_over_60 = df_truefalse[df_truefalse['wall_time'] > 60]
    df_truefalse_over_60.to_csv('./tasks/2ls_truefalse_over_60.csv', index=False)

    singlebenchtasks = []
    base = config['BASE_DIR'] + "/benchmark/sv-benchmarks/c/"

    for row in df_truefalse_over_60.itertuples(index=False):
        try:
            benchtask = parse_yml_file(base + row.inputfile)
        except Exception as e:
            print(f"Error parsing YAML file for row {row}: {e}")
            continue
        for prop_file, expected in benchtask.property_files.items():
            singlebenchtask = SingleBenchmarkTask(
                task_name="2LS",
                input_file=benchtask.input_file,
                data_model=benchtask.data_model,
                property_file=prop_file,
                expected=expected
            )
            singlebenchtasks.append(singlebenchtask)
            
        df_tasks = pd.DataFrame([task.__dict__ for task in singlebenchtasks])
        df_tasks.to_csv(f'./tasks/2ls_truefalse_benchmark_tasks_over60.csv', index=False)

# if __name__ == "__main__":
#     save_dir = './tasks/'
#     tool = '2ls'
#     if tool == 'cbmc':
#         results = parse_results_txt('./cbmc.2023-12-17_05-51-17.results.txt')
#     elif tool == '2ls':
#         results = parse_results_txt('./2ls.2023-11-30_09-35-29.results.txt')

#     results.to_csv(save_dir + tool + '_official_results.csv', index=False)
#     col = "status"
#     mask = results[col].str.lower().str.startswith(("true","false"), na=False)
#     df_filtered = results[mask]
    
#     df_filtered = df_filtered.sort_values(by='cpu_time')
#     df_filtered.to_csv(save_dir + tool + '_truefalse_results.csv', index=False)

#     df_truefalse_over_10 = df_filtered[(df_filtered['cpu_time'] >= 10.0) & (df_filtered['cpu_time'] < 100.0)]
#     df_truefalse_over_10.to_csv(save_dir + tool + '_truefalse_over_10.csv', index=False)

#     df_truefalse_over_100 = df_filtered[(df_filtered['cpu_time'] >= 100.0) & (df_filtered['cpu_time'] < 500.0)]
#     df_truefalse_over_100.to_csv(save_dir + tool + '_truefalse_over_100.csv', index=False)

#     df_truefalse_over_500 = df_filtered[df_filtered['cpu_time'] >= 500.0]
#     df_truefalse_over_500.to_csv(save_dir + tool + '_truefalse_over_500.csv', index=False)

#     base = config['BASE_DIR'] + "/benchmark/sv-benchmarks/c/"
#     for i, df in enumerate([df_truefalse_over_10, df_truefalse_over_100, df_truefalse_over_500]):
#         singlebenchtasks = []
#         for row in df.itertuples(index=False):
#             try:
#                 benchtask = parse_yml_file(base + row.inputfile)
#             except Exception as e:
#                 print(f"Error parsing YAML file for row {row}: {e}")
#                 continue
#             for prop_file, expected in benchtask.property_files.items():
#                 singlebenchtask = SingleBenchmarkTask(
#                     task_name=tool.upper(),
#                     input_file=benchtask.input_file,
#                     data_model=benchtask.data_model,
#                     property_file=prop_file,
#                     expected=expected
#                 )
#                 singlebenchtasks.append(singlebenchtask)
    
#         df_tasks = pd.DataFrame([task.__dict__ for task in singlebenchtasks])
#         threshold = [10, 100, 500][i]
#         df_tasks.to_csv(f'{save_dir}{tool}_truefalse_benchmark_tasks_over{threshold}.csv', index=False)




# if __name__ == "__main__":
#     benchmark_sets = (extract_benchmark_set(config['BASE_DIR']+ '/benchmark/benchmark-defs/cbmc.xml'))

#     #print("Benchmark Sets:")
#     #for benchmark_set in benchmark_sets:
#     #    print(f"Task Name: {benchmark_set.task_name}, Set File: {benchmark_set.set_file}, Property File: {benchmark_set.property_file}")
#     rows = []
#     for benchmark_set in benchmark_sets:
#         tasks = parse_benchmark_set(benchmark_set, single_property=True)
#         print(f"Tasks for {benchmark_set.task_name}:")
#         for task in tasks:
#             if list(task.property_files.keys()):
#                 rows.append([
#                     task.task_name,
#                     task.input_file,
#                     task.data_model,
#                     list(task.property_files.keys())[0],
#                     list(task.property_files.values())[0]
#                 ])
#             else:
#                 print(f"No property files found for task: {task.property_files}")
#     df = pd.DataFrame(rows, columns=['task_name', 'input_file', 'data_model', 'property_file', 'expected'])
#     df.to_csv('benchmark_tasks2.csv', index=False)
#         #print(df)

#            # print(f"Input File: {task.input_file}\n Data Model: {task.data_model}\n Property Files: {task.property_files}\n Task Name: {task.task_name}\n")