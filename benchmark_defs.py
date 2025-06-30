import os
import re
import glob
from dataclasses import dataclass
import yaml
from typing import Dict, Any, List, Optional, Union 

with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

@dataclass
class SingleBenchmarkResult:
    input_file: str
    property_file: str
    expected: str
    data_model: int
    exit_code: str
    last_line: str
    compile_time: float
    sat_time: float
    processing_time: float
    total_runtime: float

@dataclass
class BenchmarkSet:
    task_name: str
    set_file: str
    property_file: str

@dataclass
class SingleBenchmarkTask:
    input_file: str
    data_model: int
    property_files: Dict[str, str] = None
    task_name: str = None


def parse_yml_file(yml_file: str, single_property: str = None) -> SingleBenchmarkTask:

    base_dir = os.path.dirname(yml_file)
    base_dir_prop = os.path.dirname(base_dir)

    with open(yml_file, 'r') as file:
        data = yaml.safe_load(file)

    task = SingleBenchmarkTask(input_file='', data_model=32, property_files={})

    if 'input_files' in data:
        task.input_file = os.path.join(base_dir, data['input_files'])

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
                property_files[os.path.join(base_dir_prop, property_relative_path)] = prop['expected_verdict']

        if property_files:
            task.property_files = property_files

    return task

def parse_benchmark_set(benchmark_set: BenchmarkSet, single_property: bool = True) -> List[SingleBenchmarkTask]:

    set_file = config['BASE_DIR'] + "/benchmark/sv-benchmarks/" + benchmark_set.set_file
    tasks: List[SingleBenchmarkTask] = []
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

if __name__ == "__main__":
    benchmark_sets = (extract_benchmark_set(BASE_DIR + '/benchmark/benchmark-defs/cbmc.xml'))
    #print("Benchmark Sets:")
    #for benchmark_set in benchmark_sets:
    #    print(f"Task Name: {benchmark_set.task_name}, Set File: {benchmark_set.set_file}, Property File: {benchmark_set.property_file}")
    for benchmark_set in benchmark_sets[:1]:
        tasks = parse_benchmark_set(benchmark_set, single_property=True)
        print(f"Tasks for {benchmark_set.task_name}:")
        for task in tasks:
            print(f"Input File: {task.input_file}\n Data Model: {task.data_model}\n Property Files: {task.property_files}\n Task Name: {task.task_name}\n")