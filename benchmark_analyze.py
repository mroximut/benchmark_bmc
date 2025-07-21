from benchmark_run import *
import numpy as np

def invalid(exit_code):
    return exit_code != 10 and exit_code != 0

def compare_csv_files(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Compare exit codes for each row
    for idx in range(len(df2)):
        val1 = df1.loc[idx, 'exit_code']
        val2 = df2.loc[idx, 'exit_code']

        if val1 != val2 and not (invalid(val1) and invalid(val2)):
            print(f"\nDifference in row {idx} ({df1.loc[idx, 'input_file']}):")
            print(f"  exit_code: {val1} vs {val2}")

def plot_instances_solved_across_runtime(files: List[str], filename: str = 'instances_solved_vs_runtime.png'):
    plt.close('all')
    for file in files:
        df = pd.read_csv(file)
        # Use 'total_runtime' as x, filter only solved instances (exit_code == 0 or 10)
        solved = df[df['exit_code'].isin([0, 10])].copy()
        solved_times = np.sort(solved['processing_time'].astype(float).values)
        y = np.arange(1, len(solved_times) + 1)
        plt.step(solved_times, y, where='post', label=file.split('/')[-1])

    plt.xlabel('Time (s)')
    plt.ylabel('Instances solved')
    plt.title('Instances solved vs. runtime')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.xscale('log')
    plt.savefig(os.path.join(os.path.dirname(files[0]), filename))

def speedup_values(file1, file2, threshold=0):
    with open(file2.replace('.csv', '_speedups.txt'), 'a') as f:
        f.write(f"Speedups for {file1} vs {file2}:\n")
        speedups = []
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        for idx in range(len(df1)):
            if df1.loc[idx, 'exit_code'] == 0 and df2.loc[idx, 'exit_code'] == 0 or \
            df1.loc[idx, 'exit_code'] == 10 and df2.loc[idx, 'exit_code'] == 10:
                time1 = df1.loc[idx, 'processing_time']
                time2 = df2.loc[idx, 'processing_time']
                task_name, input_file, data_model, property_file, expected = df1.loc[idx, ['task_name', 'input_file', 'data_model', 'property_file', 'expected']]
                if time1 > threshold and time2 > threshold:
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

    base = "./test_all200/"
    #compare_csv_files(base + "results/cbmc_results.csv",
    #                    base +"results/mallob-cbmc_results.csv",
    #                    base + "results/mallob-parallel-cbmc_results.csv")
    #plot_instances_solved_across_runtime([base + "results/cbmc_results.csv",
    #                    base + "results/mallob-cbmc_results.csv",
    #                    base + "results/mallob-parallel-cbmc_results.csv"], "instances_solved_vs_runtime_cbmc.png")
    speedups = speedup_values(base + "results/cbmc_results.csv",
                               base + "results/mallob-cbmc_results.csv")
    
    print(f"Speedups: {sorted(speedups)}")
    geometric_mean = np.exp(np.mean(np.log(speedups)))
    print(f"Geometric mean of speedups: {geometric_mean:.2f}")
   