from benchmark_run import *
import numpy as np
from itertools import cycle
import matplotlib.pyplot as plt

def invalid(exit_code):
    return exit_code != 10 and exit_code != 0 and exit_code != 42

def compare_csv_files(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Compare exit codes for each row
    for idx in range(len(df1)):
        val1 = df1.loc[idx, 'exit_code']
        val2 = df2.loc[idx, 'exit_code']

        if val1 != val2 and not (invalid(val1) and invalid(val2)):
            print(f"\nDifference in row {idx} ({df1.loc[idx, 'input_file']}):")
            print(f"  exit_code: {val1} vs {val2}")

def plot_instances_solved_across_runtime(files: List[str], filename: str = 'instances_solved_vs_runtime.png', first_n = None):
    plt.close('all')

    # color-blind friendly palette (manual, no seaborn)
    palette = [
        "#0072B2",  # blue
        "#D55E00",  # vermilion
        "#CC79A7",  # magenta
        "#F0E442",  # yellow
        "#56B4E9",  # sky blue
        "#E69F00",  # orange
        "#000000",  # black
    ]
    colors = cycle(palette)

    # Different line styles for different solvers
    linestyles_list = [
        '-', '--', '-.', ':',
        (0, (5, 1)),    # long dash + gap
        (0, (3, 1, 1, 1)),  # dash-dot pattern
        (0, (1, 1)),    # densely dashed
        (0, (1, 2)),    # sparse dashed
    ]
    line_styles = cycle(linestyles_list)

    for file in files:
        df = pd.read_csv(file)
        # Use 'total_runtime' as x, filter only solved instances (exit_code == 0 or 10)
        if first_n is not None:
            df = df.head(first_n)
        solved = df[df['exit_code'].isin([0, 10, 42])].copy()
        solved_times = np.sort(solved['processing_time'].astype(float).values)
        y = np.arange(1, len(solved_times) + 1)

        # Extend each curve horizontally to 900s
        if len(solved_times) > 0:
            solved_times = np.append(solved_times, 900.0)
            y = np.append(y, y[-1])
            
        plt.step(
            solved_times, y, where='post', label=file.split('/')[-1].split('_results.csv')[0], 
            color=next(colors), linestyle=next(line_styles), linewidth=1.5)

    plt.xlabel('Time (s)')
    plt.ylabel('Instances solved')
    plt.title('Instances solved vs. runtime')
    plt.legend()
    plt.grid(True)
    plt.xlim(0, 900)
    plt.tight_layout()
    #plt.xscale('log')
    #plt.grid(which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.savefig(os.path.join(os.path.dirname(files[0]), filename), dpi=300, bbox_inches='tight')
    plt.show()

def speedup_values(file1, file2, threshold=0):
    with open(file2.replace('.csv', '_speedups.txt'), 'a') as f:
        f.write(f"Speedups for {file1} vs {file2}:\n")
        speedups = []
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        for idx in range(len(df1)):
            if df1.loc[idx, 'exit_code'] == 0 and df2.loc[idx, 'exit_code'] == 0 or \
            df1.loc[idx, 'exit_code'] == 10 and df2.loc[idx, 'exit_code'] == 10 or \
            df1.loc[idx, 'exit_code'] == 42 and df2.loc[idx, 'exit_code'] == 42:
            #if "TRUE" in df1.loc[idx, 'last_line'] and "TRUE" in df2.loc[idx, "last_line"] or \
            #   "FALSE" in df1.loc[idx, 'last_line'] and "FALSE" in df2.loc[idx, 'last_line']:
                time1 = df1.loc[idx, 'processing_time']
                time2 = df2.loc[idx, 'processing_time']
                task_name, input_file, data_model, property_file, expected = df1.loc[idx, ['task_name', 'input_file', 'data_model', 'property_file', 'expected']]
                #if time1 > threshold and time2 > threshold:
                speedup = time1 / time2
                f.write(f"{task_name},{input_file},{data_model},{property_file},{expected}\n")
                f.write(f"{idx}: {time1:.2f} / {time2:.2f} = {speedup:.2f}\n")
                speedups.append(speedup)
            
    return speedups
            


if __name__ == "__main__":
    # base01 = "./test_termination_reachsafety_others505050_trivial01/"
    # base = "./test_termination_reachsafety_others505050/"
    # compare_csv_files(base + "results/2ls_results.csv",
    #                     base01 +"results/mallob-2ls_results.csv")
    # plot_instances_solved_across_runtime([base + "results/2ls_results.csv",
    #                     base01 + "results/mallob-2ls_results.csv"])
    # speedups = speedup_values(base + "results/2ls_results.csv",
    #                           base01 + "results/mallob-2ls_results.csv")
    
    # print(f"Speedups: {sorted(speedups)}")
    # geometric_mean = np.exp(np.mean(np.log(speedups)))
    # print(f"Geometric mean of speedups: {geometric_mean:.2f}")

    # base = "./test_all200/"
    # compare_csv_files( base +"results/mallob-cbmc_results.csv",
    #                     base + "results/mallob-parallel-cbmc_results.csv")
    # plot_instances_solved_across_runtime([base + "results/cbmc_results.csv",
    #                     base + "results/mallob-cbmc_results.csv",
    #                     base + "results/mallob-parallel-cbmc_results.csv"], "instances_solved_vs_runtime_cbmc.png")
    # speedups = speedup_values(base + "results/mallob-cbmc_results.csv",
    #                            base + "results/mallob-parallel-cbmc_results.csv")
    
    # print(f"Speedups: {sorted(speedups)}")
    # geometric_mean = np.exp(np.mean(np.log(speedups)))
    # print(f"Geometric mean of speedups: {geometric_mean:.2f}")


    base_2ls = "./test_2ls_over_500_newstream/"
    base_cbmc = "./test_cbmc_over_500_newstream/"
    seq_cbmc = base_cbmc + "results/cbmc_results.csv"
    m32 = base_cbmc + "results/mallob-cbmc-newstream32_results.csv"
    fs32 = base_cbmc + "results/mallob-filesys32-cbmc_results.csv"
    p4x8 = base_cbmc + "results/mallob-parallel-cbmc-newstream4x8_results.csv"
    files_2ls = [base_2ls + "results/" + file for file in os.listdir(base_2ls + "results/") if file.endswith(".csv")]
    files_cbmc = [base_cbmc + "results/" + file for file in os.listdir(base_cbmc + "results/") if file in [
        "cbmc_results.csv", 
        "mallob-cbmc-newstream32_results.csv",
        "mallob-filesys32-cbmc_results.csv",
        "mallob-parallel-cbmc-newstream4x8_results.csv"
    ]]
    # for file in files_cbmc:
    #     print(f"Comparing {seq_cbmc} and {file}")
    #     print()
    #     compare_csv_files(seq_cbmc, file)
    #     print()
    #compare_csv_files(m32, p4x8)
    #plot_instances_solved_across_runtime(files_2ls, "instances_solved_vs_runtime_2ls_over500_newstream_4dec.png")
    plot_instances_solved_across_runtime(files_cbmc, "instances_solved_vs_runtime_cbmc_over500_newstream_4dec.png", first_n=150)

    # for file2 in files_2ls:
    #     speedups = speedup_values(base_2ls + "results/2ls_results.csv", file2)
    #     #print(f"Speedups for 2ls vs {file2}: {sorted(speedups)}")
    #     geometric_mean = np.exp(np.mean(np.log(speedups)))
    #     print(f" {file2.split('/')[-1].split('.')[0].split('_results')[0]} vs 2ls: {geometric_mean:.2f}")

    # for file2 in files_cbmc:
    #     speedups = speedup_values(base_cbmc + "results/cbmc_results.csv", file2)
    #     #print(f"Speedups for cbmc vs {file2}: {sorted(speedups)}")
    #     geometric_mean = np.exp(np.mean(np.log(speedups)))
    #     print(f" {file2.split('/')[-1].split('.')[0].split('_results')[0]} vs cbmc: {geometric_mean:.2f}")

