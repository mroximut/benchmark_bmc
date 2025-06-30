from benchmark_defs import *
from enum import Enum

class Solver:
    def __init__(self, name: str, command: str, filesystem: bool = False, dir: str = config['BENCHMARK_BMC']):
        self.name = name
        self.command = command
        self.filesystem = filesystem
        self.dir = dir

    def run(self, task: SingleBenchmarkTask) -> SingleBenchmarkResult:
        pass

class Solvers(Enum):
    CBMC = Solver(name="CBMC", command="cbmc-wrapper")
    TWOLS = Solver(name="TWOLS", command="2ls-wrapper")
    MALLOB_CBMC = Solver(name="MALLOB_CBMC", command="mallob-cbmc-wrapper")
    MALLOB_2LS = Solver(name="MALLOB_2LS", command="mallob-2ls-wrapper")

class BenchmarkRunner:
    def __init__(self, tasks: List[SingleBenchmarkTask], solvers: List[Solver], save_directory: str):
        self.tasks = tasks
        self.solvers = solvers
        self.save_directory = save_directory
    
    def run(self):
        pass 