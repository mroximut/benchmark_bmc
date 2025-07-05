import subprocess
import time
from benchmark_defs import *
from enum import Enum
import random 

class SolverType(Enum):
    CBMC = "cbmc"
    TWOLS = "2ls"
    MALLOB_CBMC = "mallob-cbmc"
    MALLOB_2LS = "mallob-2ls"
    MALLOB_CBMC_FILESYSTEM = "mallob-cbmc-filesystem"
    MALLOB_2LS_FILESYSTEM = "mallob-2ls-filesystem"


class Solver:
    def __init__(self, type: SolverType, dir: str = "./", save_dir: str = "./", sv_benchmarks_dir: str = "../benchmark/sv-benchmarks/"):
        self.type = type
        self.command = type.value + '-wrapper'
        self.dir = dir
        self.save_dir = save_dir
        self.sv_benchmarks_dir = sv_benchmarks_dir
        self.result = None

    def run(self, task: SingleBenchmarkTask, timeout: float = config['TIMEOUT'], log: bool = True) -> SingleBenchmarkResult:
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
        print(f"Running command: {' '.join(subprocess_command)}")
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
                last_lines = output_lines[-min(15, len(output_lines)):]
                result.last_line = last_lines[-1] if last_lines else ""
                for line in last_lines:
                    if 't COMPILE_TIME' in line:
                        result.compile_time = float(line.split(':')[-1].strip())
                    elif 't FINAL SAT_TIME' in line:
                        result.sat_time = float(line.split(':')[-1].strip())
                    elif 't PROCESSING_TIME' in line:
                        result.processing_time = float(line.split(':')[-1].strip())
                    elif 's FINAL EC' in line:
                        result.exit_code = int(line.split('=')[-1].strip())
                    elif 't FINAL SAT_CALLS' in line:
                        result.sat_calls = int(line.split(':')[-1].strip())
            self.result = result
                
            if res and log:
                self.save_log(res.stdout, self.save_dir)

            self.cleanup()

        return result 

    def cleanup(self):
        commands = []
        if self.type == SolverType.CBMC:
            commands.append("pkill -f cbmc")
        elif self.type == SolverType.TWOLS:
            commands.append("pkill -f 2ls")
        elif self.type in  [SolverType.MALLOB_CBMC, SolverType.MALLOB_2LS]:
            commands.extend(["pkill -f mallob", "pkill -f MainThread", "pkill -f mpirun", "pkill -f mallob_sat_process"])

        for command in commands:
            try:
                subprocess.run(command, shell=True, check=True)
            except Exception as e:
                print(f"{e}")

    def save_log(self, stdout:str, save_dir: str):
        log_file = os.path.join(save_dir, "logs", f"{self.type.value}_logs", f"{self.result.task.task_name}_{self.result.task.input_file.replace('/', '_')}.log")
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
        save_path = os.path.join(save_dir, "results", f"{self.type.value}_results.csv")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        if os.path.exists(save_path):
            df.to_csv(save_path, mode='a', header=False, index=False)
        else:
            df.to_csv(save_path, index=False)        


class BenchmarkRunner:
    def __init__(self, tasks: List[SingleBenchmarkTask], solvers: List[SolverType], save_directory: str):
        self.tasks = tasks
        self.solvers = [Solver(type=solver_type, dir="./", save_dir=save_directory) for solver_type in solvers]
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)
        self.seed = None
    
    def run(self, timeout: int, log: bool):
        for task in self.tasks:
            for solver in self.solvers:
                print(f"Running {solver.type.value} on task {task.task_name}...")
                result = solver.run(task, timeout=timeout, log=log)
                print(f"Result for {task.task_name} with {solver.type.value}: {result.exit_code}, in {result.processing_time}s from which {result.sat_time}s SAT.")
                solver.save_to_csv()

    def set_tasks_randomly(self, no_tasks: int, all_tasks_csv: str = "benchmark_tasks.csv", seed: int = 42):
        self.seed = seed
        df = pd.read_csv(all_tasks_csv)
        random.seed(seed)
        selected_rows = df.sample(n=no_tasks, random_state=seed)
        
        self.tasks = [
            SingleBenchmarkTask(
                task_name=row['task_name'],
                input_file=row['input_file'],
                data_model=row['data_model'],
                property_file=row['property_file'],
                expected=row['expected']
            ) for _, row in selected_rows.iterrows()
        ]
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
        
        df.to_csv(os.path.join(self.save_directory, save_file), index=False)
        print(f"Saved {len(self.tasks)} with seed {self.seed if self.seed else ""} tasks to {save_file}.")

    def load_tasks_from_csv(self, csv_file: str):
        df = pd.read_csv(csv_file)
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

if __name__ == "__main__":
    # task = SingleBenchmarkTask(
    #     task_name="test",
    #     input_file="./test_programs/dijkstra-u_unwindbound50.c",
    #     data_model=32,
    #     property_file="./test_programs/valid-memsafety.prp",
    #     expected=True
    # )
    # solver = Solver(SolverType.TWOLS)
    # solver.run(task, timeout=60, log=True)
    # solver.save_to_csv()
    
    runner = BenchmarkRunner([], [SolverType.TWOLS, SolverType.MALLOB_2LS], save_directory='./test')
    runner.set_tasks_randomly(no_tasks=2, all_tasks_csv='benchmark_tasks.csv', seed=123)
    #runner.save_tasks_to_csv()
    
    runner.run(timeout=10, log=True)