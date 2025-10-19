import shutil
import subprocess
import time
from benchmark_defs import *
from enum import Enum
import random 
import sys
import os
import matplotlib.pyplot as plt

class SolverType(Enum):
    CBMC = "cbmc"
    TWOLS = "2ls"
    MALLOB_CBMC = "mallob-cbmc"
    MALLOB_PARALLEL_CBMC = "mallob-parallel-cbmc"
    MALLOB_2LS = "mallob-2ls"
    MALLOB_CBMC_FILESYSTEM = "mallob-filesys-cbmc"
    #MALLOB_2LS_FILESYSTEM = "mallob-2ls-filesystem"
    MALLOB_2LS_1THREAD = "mallob-2ls-1thread"


class Solver:
    def __init__(self, type: SolverType, dir: str = "./", save_dir: str = "./", sv_benchmarks_dir: str = "../benchmark/sv-benchmarks/", postfix: str = ""):
        self.type = type
        self.command = type.value + '-wrapper'
        self.dir = dir
        self.save_dir = save_dir
        self.sv_benchmarks_dir = sv_benchmarks_dir
        self.result = None
        self.postfix = postfix

    def run(self, task: SingleBenchmarkTask, timeout: float = config['TIMEOUT'], log: bool = True, check_csv: bool = False, dry: bool = False, dump_cnf: bool = False) -> SingleBenchmarkResult:
        if not dry:
            self.cleanup()
        
        if check_csv:
            csv_file = os.path.join(self.save_dir, "results", f"{self.type.value + self.postfix}_results.csv")
            result = self.get_result_from_csv(csv_file, task)
            if result:
                print(f"Result found in CSV for task {task.task_name}: {result.exit_code}, in {result.processing_time}s from which {result.sat_time}s SAT.")
                return result
        
        result = SingleBenchmarkResult(
            task=task,
            exit_code=None,
            last_line=None,
            compile_time=None,
            sat_time=None,
            processing_time=None,
            total_runtime=None,
            sat_calls=None,
        )
        
        subprocess_command = [
            self.dir + self.command,
            self.sv_benchmarks_dir + task.input_file,
            '--propertyfile', self.sv_benchmarks_dir + task.property_file,
            '--' + str(task.data_model)
        ]
        if dump_cnf:    
            subprocess_command.append('--dump-cnf')
            subprocess_command.append(task.input_file.replace('/', '_') + '.cnf')

        print(f"Running command: {' '.join(subprocess_command)}")
        if dry:
            print("Dry run mode: not executing the command.")
            return
        start = time.time()
        res = None

        try:
            res = subprocess.run(subprocess_command, 
                             capture_output=True,
                             text=True, 
                             cwd=self.dir,
                             timeout=timeout)
            
        except subprocess.TimeoutExpired as e:
            print(f"Timeout: {' '.join(subprocess_command)}")
            result.exit_code = -1
            result.last_line = str(e)
            
        except KeyboardInterrupt:
            print("Process interrupted by user.")
            self.cleanup()
            exit(0)
  
        except Exception as e:
            print(f"Error running command: {' '.join(subprocess_command)}")
            print(f"Error: {str(e)}")
            result.exit_code = -2
            result.last_line = str(e)
        
        finally:
            result.total_runtime = time.time() - start
            if res and res.stdout:
                output_lines = res.stdout.strip().split('\n')
                last_lines = output_lines[-min(50, len(output_lines)):]
                result.last_line = last_lines[-1] if last_lines else ""
                for line in last_lines:
                    try: 
                        if 't COMPILE_TIME' in line:
                            result.compile_time = float(line.split(':')[-1].strip())
                        elif 't FINAL SAT_TIME' in line:
                            result.sat_time = float(line.split(':')[-1].strip())
                        elif 't FINAL PROCESSING_TIME' in line:
                            result.processing_time = float(line.split(':')[-1].strip())
                        elif 's FINAL EC' in line:
                            result.exit_code = int(line.split('=')[-1].strip())
                        elif 't FINAL SAT_CALLS' in line:
                            result.sat_calls = int(line.split(':')[-1].strip())
                    except Exception as e:
                        print(f"Error parsing line: {line} with error {e}")
                        continue

            else:
                print("No output from the solver.")
                if not result.exit_code:
                    result.exit_code = -3
                if not result.last_line:
                    result.last_line = "No output from the solver."
            
            self.result = result
                
            if log and res and res.stdout:
                self.save_log(res.stdout, self.save_dir)

            self.cleanup()

        return result 

    def cleanup(self):
        commands = []
        #if self.type == SolverType.CBMC:
        #    commands.append("pkill -f cbmc")
        #elif self.type == SolverType.TWOLS:
        #    commands.append("pkill -f 2ls")
        #elif self.type in  [SolverType.MALLOB_CBMC, SolverType.MALLOB_2LS, SolverType.MALLOB_PARALLEL_CBMC]:
        commands.extend(["pkill -f cbmc","pkill -f 2ls","pkill -f mallob", "pkill -f MainThread", "pkill -f mpirun", "pkill -f mallob_sat_process", "tmux kill-session -t mallob_filesystem"])
        time.sleep(1)
        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True)
            except Exception as e:
                print(f"{e}")
        time.sleep(1)

    def save_log(self, stdout:str, save_dir: str):
        log_file = os.path.join(save_dir, "logs", f"{self.type.value + self.postfix}_logs", f"{self.result.task.task_name}_{self.result.task.input_file.replace('/', '_')}_{self.result.task.property_file.split('/')[-1].replace('.prp', '')}.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write(stdout)
        

    def save_to_csv(self, save_dir: str = None):
        if not self.result:
            print("No result to save.")
            return
        
        if save_dir is None:
            save_dir = self.save_dir
        
        df = pd.DataFrame([{
            'task_name': self.result.task.task_name,
            'input_file': self.result.task.input_file,
            'data_model': self.result.task.data_model,
            'property_file': self.result.task.property_file,
            'expected': self.result.task.expected,
            'exit_code': self.result.exit_code,
            'compile_time': self.result.compile_time,
            'sat_time': self.result.sat_time,
            'processing_time': self.result.processing_time,
            'total_runtime': self.result.total_runtime,
            "sat_calls": self.result.sat_calls,
            'last_line': self.result.last_line,
        }])
        save_path = os.path.join(save_dir, "results", f"{self.type.value + self.postfix}_results.csv")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        if os.path.exists(save_path):
            df.to_csv(save_path, mode='a', header=False, index=False)
        else:
            df.to_csv(save_path, index=False)   

    def get_result_from_csv(self, csv_file: str, single_task: SingleBenchmarkTask) -> SingleBenchmarkResult:
        df = pd.read_csv(csv_file)
        task_df = df[(df['task_name'] == single_task.task_name) & 
                     (df['input_file'] == single_task.input_file) & 
                     (df['data_model'] == single_task.data_model) & 
                     (df['property_file'] == single_task.property_file)]
        
        if task_df.empty:
            print(f"No result found for task {single_task.task_name} in {csv_file}.")
            return None
        
        row = task_df.iloc[0]
        result = SingleBenchmarkResult(
            task=single_task,
            exit_code=row['exit_code'],
            compile_time=row['compile_time'],
            sat_time=row['sat_time'],
            processing_time=row['processing_time'],
            total_runtime=row['total_runtime'],
            sat_calls=row['sat_calls'],
            last_line=row['last_line']
        )
        return result



class BenchmarkRunner:
    def __init__(self, tasks: List[SingleBenchmarkTask], solvers: List[SolverType], save_directory: str):
        self.tasks = tasks
        self.solvers = [Solver(type=solver_type, dir="./", save_dir=save_directory) for solver_type in solvers]
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)
        self.seed = None
        self.category = []

    def run(self, timeout: int, log: bool, dry_run: bool = False, dump_cnf: bool = False):
        with open(os.path.join(self.save_directory, "info.txt"), 'a') as f:
            f.write(f"Seed: {self.seed}\n")
            f.write(f"Timeout: {timeout} seconds\n")
            f.write(f"Tasks: {len(self.tasks)}\n")
            f.write(f"Solvers: {[solver.type.value for solver in self.solvers]}\n")
            f.write(f"Categories: {self.category}\n")
        
        if dry_run:
            return

        for task in self.tasks:
            for solver in self.solvers:
                print(f"Running {solver.type.value} on task {task.task_name}...")
                result = solver.run(task, timeout=timeout, log=log, dump_cnf=dump_cnf)
                print(f"Result for {task.task_name} with {solver.type.value}: {result.exit_code}, in {result.processing_time}s from which {result.sat_time}s SAT.")
                solver.save_to_csv()

    def set_tasks_randomly(self, no_tasks: int, all_tasks_csv: str = "benchmark_tasks.csv", seed: int = 42, category: List[str] = [], exclude: List[str] = []):
        self.seed = seed
        self.category = category 
        df = pd.read_csv(all_tasks_csv)
        random.seed(seed)

        if category:
            df = df[df['task_name'].apply(lambda x: any(x.lower().startswith(cat.lower()) for cat in category))]

        no_tasks = min(no_tasks, len(df))
        selected_rows = df.sample(n=no_tasks, random_state=seed)

        if exclude:
            selected_rows = selected_rows[~selected_rows['input_file'].isin(exclude)]
            no_tasks = min(no_tasks, len(selected_rows))
        
        self.tasks.extend([
            SingleBenchmarkTask(
                task_name=row['task_name'],
                input_file=row['input_file'],
                data_model=row['data_model'],
                property_file=row['property_file'],
                expected=row['expected']
            ) for _, row in selected_rows.iterrows()
        ])
        print(f"Selected {len(self.tasks)} tasks randomly from {all_tasks_csv}.")

    def save_tasks_to_csv(self, save_file: str = "tasks.csv"):
        if not self.tasks:
            print("No tasks to save.")
            return
        
        df = pd.DataFrame([{
            'task_name': task.task_name,
            'input_file': task.input_file,
            'data_model': task.data_model,
            'property_file': task.property_file,
            'expected': task.expected,
        } for task in self.tasks])
        
        csv_path = os.path.join(self.save_directory, save_file)
        file_exists = os.path.exists(csv_path)
        df.to_csv(csv_path, mode='a', header=not file_exists, index=False)
        
        seed_tmp = self.seed if self.seed else ""
        print(f"Saved {len(self.tasks)} with seed {seed_tmp} tasks to {save_file}.")


    def load_tasks_from_csv(self, csv_file: str = "tasks.csv"):
        csv_path = os.path.join(self.save_directory, csv_file)
        file_exists = os.path.exists(csv_path)
        if not file_exists:
            print(f"No tasks file found at {csv_path}. Please save tasks first.")
            return
        print(f"Loading tasks from {csv_file}...")
        df = pd.read_csv(csv_path)
        self.tasks = [
            SingleBenchmarkTask(
                task_name=row['task_name'],
                input_file=row['input_file'],
                data_model=row['data_model'],
                property_file=row['property_file'],
                expected=row['expected']
            ) for _, row in df.iterrows()
        ]
        print(f"Loaded {len(self.tasks)} tasks from {csv_file}.")


def str_to_task(task_str: str) -> SingleBenchmarkTask:
    parts = task_str.split(',')
    if len(parts) != 5:
        raise ValueError(f"Invalid task string format: {task_str}")
    
    return SingleBenchmarkTask(
        task_name=parts[0].strip(),
        input_file=parts[1].strip(),
        data_model=int(parts[2].strip()),
        property_file=parts[3].strip(),
        expected=parts[4].strip().lower() == 'true'
    )

if __name__ == "__main__":
    # runner = BenchmarkRunner([], [SolverType.MALLOB_2LS_1THREAD, SolverType.MALLOB_2LS], save_directory=f'./test_2ls_over_500/')
    runner = BenchmarkRunner([], [SolverType.MALLOB_CBMC, SolverType.MALLOB_PARALLEL_CBMC], save_directory=f'./test_cbmc_over_500/')
    # runner = BenchmarkRunner([], [SolverType.MALLOB_CBMC_FILESYSTEM], save_directory=f'./test_cbmc_over_500/')
    runner.load_tasks_from_csv()
    runner.run(timeout=900, log=True, dry_run=False)