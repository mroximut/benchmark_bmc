    # task = SingleBenchmarkTask(
    #     task_name="test",
    #     input_file="test_programs/elevator_spec14_product03.cil.c",
    #     #input_file="test_programs/dijkstra-u_unwindbound50.c",
    #     data_model=32,
    #     #property_file="test_programs/valid-memsafety.prp",
    #     property_file="test_programs/termination.prp",
    #     expected=True
    # )
    # solver = Solver(SolverType.TWOLS, sv_benchmarks_dir="./")
    # solver.run(task, timeout=60, log=True)
    # solver.save_to_csv()
    #task = str_to_task("MemSafety-Juliet,c/Juliet_Test/CWE401_Memory_Leak---s03---CWE401_Memory_Leak__struct_twoIntsStruct_malloc_34_good.i,64,c/properties/valid-memsafety.prp,True")
    #task2 = str_to_task("ReachSafety-Combinations,c/combinations/square_5+soft_float_1-2a.c.cil.c,32,c/properties/unreach-call.prp,True")
    #task3 = str_to_task("ReachSafety-Recursive,c/recursive-simple/fibo_25-1.c,32,c/properties/unreach-call.prp,False")
    #task4 = str_to_task("NoOverflows-Main,c/nla-digbench-scaling/lcm1_valuebound20.c,32,c/properties/no-overflow.prp,True")
    #task5 = str_to_task("ReachSafety-ECA,c/eca-rers2012/Problem14_label28.c,32,c/properties/unreach-call.prp,False")
    #print(Solver(SolverType.MALLOB_PARALLEL_CBMC).run(task4, timeout=60, log=True, dry=True))
    
    # tool = "2ls"
    # all_selected_tasks = []
    # random.seed(42)
    # for threshold in [10, 100, 500]:
    #     csv_file = f"./tasks/{tool}_truefalse_benchmark_tasks_over{threshold}.csv"
    #     df = pd.read_csv(csv_file)
    #     num_to_select = min(25, len(df))
    #     selected_rows = df.sample(n=num_to_select)
    #     all_selected_tasks.append(selected_rows)

    # combined_df = pd.concat(all_selected_tasks, ignore_index=True)

    # output_csv = f"./tasks/{tool}_combined_tasks.csv"
    # combined_df.to_csv(output_csv, index=False)

    # print(f"Selected and combined {len(combined_df)} tasks, saved to {output_csv}")

    #runner = BenchmarkRunner([], [SolverType.TWOLS, SolverType.MALLOB_2LS], save_directory=f'./test_2ls_252525/')
    #runner.load_tasks_from_csv()
    #runner.run(timeout=900, log=True, dry_run=False)






    # csv_file = f"./tasks/2ls_truefalse_benchmark_tasks_over60.csv"
    # df = pd.read_csv(csv_file)
    # # Load the already sampled 300
    # sampled_300 = pd.read_csv("./test_over60_2ls/tasks copy.csv")
    # already_sampled_files = set(sampled_300['input_file'])

    # # Exclude the already sampled 300
    # remaining_df = df[~df['input_file'].isin(already_sampled_files)]

    # # Sample 200 new instances
    # sampled_200 = remaining_df.sample(n=200, random_state=42)

    # # Save the new 200
    # sampled_200.to_csv("./test_over60_2ls/tasks_extra200.csv", index=False)    
    #selected_rows = df.sample(n=500)
    #combined_df = pd.concat([selected_rows], ignore_index=True)
    #combined_df.to_csv(f"./test_over60_2ls/tasks.csv", index=False)



    ##runner = BenchmarkRunner([], [SolverType.TWOLS], save_directory=f'./test_over60_2ls/')
    ##runner.load_tasks_from_csv()
    ##runner.run(timeout=900, log=True, dry_run=False, dump_cnf=True)

    # j = 0

    #######results_df = pd.read_csv('./test_over60_2ls/results/2ls_results.csv')
    
    # for row in results_df.itertuples():
    #     if row.total_runtime < 30 and \
    #     (os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}.cnf') or os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_term.cnf') or os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_nonterm.cnf')):
    #         j += 1  
        # if row.property_file == 'c/properties/termination.prp':
        #     if 'TRUE' in row.last_line.upper():
        #         if not os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}.cnf_term'):
        #             if not os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_term.cnf'):
        #                 print(f"Whats happening? File not found: ./cnf/{row.input_file.replace('/', '_')}.cnf_term")
        #             continue
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_term', f'./cnf/{row.input_file.replace("/", "_")}_term.cnf')
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_nonterm', f'./cnf_discard/{row.input_file.replace("/", "_")}.cnf_nonterm')
        #     elif 'FALSE' in row.last_line.upper():
        #         if not os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}.cnf_nonterm'):
        #             if not os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_nonterm.cnf'):
        #                 print(f"Whats happening? File not found: ./cnf/{row.input_file.replace('/', '_')}.cnf_nonterm")
        #             continue
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_nonterm', f'./cnf/{row.input_file.replace("/", "_")}_nonterm.cnf')
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_term', f'./cnf_discard/{row.input_file.replace("/", "_")}.cnf_term')
        #     else:
        #         print(f"Unknown result for {row.input_file}: {row.last_line}")
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_term', f'./cnf_discard/{row.input_file.replace("/", "_")}.cnf_term')
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf_nonterm', f'./cnf_discard/{row.input_file.replace("/", "_")}.cnf_nonterm')
        # if not "TRUE" in row.last_line.upper() and not "FALSE" in row.last_line.upper():
        #     print(f"Unknown result for {row.input_file}")
        #     if os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}.cnf'):
        #         shutil.move(f'./cnf/{row.input_file.replace("/", "_")}.cnf', f'./cnf_discard/{row.input_file.replace("/", "_")}.cnf')

    # for row in results_df[::-1].itertuples():
    #     if not os.path.exists(f'./cnf_new/{row.input_file.replace("/", "_")}_termination.cnf') or row.property_file == 'c/properties/termination.prp':
    #         continue
    #     assert("TRUE" in row.last_line.upper() or "FALSE" in row.last_line.upper())

    #     property_suffix = row.property_file.split('/')[-1].replace('.prp', '')
    #     shutil.move(f'./cnf_new/{row.input_file.replace("/", "_")}_termination.cnf', f'./cnf_new/{row.input_file.replace("/", "_")}_{property_suffix}.cnf')
    #     print(f'Moved ./cnf_new/{row.input_file.replace("/", "_")}_termination.cnf to ./cnf_new/{row.input_file.replace("/", "_")}_{property_suffix}.cnf')
    




    # unknown_rows = []
    # for row in results_df[::-1].itertuples():
    #     file_suffix = None
    #     finishing_option = None
    #     if not row.property_file == 'c/properties/termination.prp':
    #         continue
    #     if os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_term.cnf'):
    #         file_suffix = 'term'
    #     elif os.path.exists(f'./cnf/{row.input_file.replace("/", "_")}_nonterm.cnf'):
    #         file_suffix = 'nonterm'
    #     else:
    #         #print(f"CNF file missing for {row.input_file}")
    #         continue
    #     if not os.path.exists(f'./test_over60_2ls/logs/2ls_logs/{row.task_name}_{row.input_file.replace("/", "_")}.log'):
    #         print(f"Log file missing for {row.input_file}")
    #         continue
    #     file_to_open = None 
    #     new_generated = f'./test_over60_2ls/logs/2ls_logs/{row.task_name}_                                 {row.input_file.replace("/", "_")}_termination.log'
    #     if os.path.exists(new_generated):
    #         file_to_open = new_generated
    #     else:  
    #         file_to_open = f'./test_over60_2ls/logs/2ls_logs/{row.task_name}_{row.input_file.replace("/", "_")}.log'
    
    #     with open(file_to_open, 'r') as log_file:
    #         for line in log_file:
    #             if 'argv[5]' in line:
    #                 if '--termination' in line:
    #                     finishing_option = 'term'
    #                 elif '--nontermination' in line:
    #                     finishing_option = 'nonterm'
    #                 else:
    #                     pass
    #                     print(f"Unknown finishing option in log for {row.input_file}")
    #                     unknown_rows.append(row)
    #                 break   
    #     if not finishing_option:
    #         continue
    #     if finishing_option != file_suffix:
    #         #pass
    #         print(f"Mismatch for {row.input_file}: file_suffix={file_suffix}, finishing_option={finishing_option}")
    #     else:
    #         pass
    #         #print(f"Match for {row.input_file}: {file_suffix}")

    # # Convert unknown_rows to DataFrame and save as CSV
    # if unknown_rows:
    #     unknown_df = pd.DataFrame([{
    #         'task_name': row.task_name,
    #         'input_file': row.input_file,
    #         'data_model': row.data_model,
    #         'property_file': row.property_file,
    #         'expected': row.expected
    #     } for row in unknown_rows])
        
    #     unknown_df.to_csv('./unknown_finishing_option_rows.csv', index=False)
    #     print(f"Saved {len(unknown_rows)} rows with unknown finishing option to CSV")
    # else:
    #     print("No rows with unknown finishing option found")





    #runner = BenchmarkRunner([], [SolverType.MALLOB_CBMC, SolverType.MALLOB_PARALLEL_CBMC], save_directory='./test_all200/')
    #runner.load_tasks_from_csv()
    #runner.run(timeout=900, log=True, dry_run=False)

    #df_exclude = pd.read_csv('./test_termination_reachsafety_others505050/tasks.csv')
    #exclude = df_exclude['input_file'].tolist()
    
    #runner.set_tasks_randomly(no_tasks=50, all_tasks_csv='benchmark_tasks.csv', seed=42424242, category=['MemSafety'])
    #runner.set_tasks_randomly(no_tasks=50, all_tasks_csv='benchmark_tasks.csv', seed=42424242, category=['NoOverflows'])
    #runner.set_tasks_randomly(no_tasks=50, all_tasks_csv='benchmark_tasks.csv', seed=42424242, category=['SoftwareSystems'])

    #runner.set_tasks_randomly(no_tasks=200, all_tasks_csv='benchmark_tasks.csv', seed=123456)
    
    #runner.save_tasks_to_csv()
    
    #runner.run(timeout=900, log=True, dry_run=False)