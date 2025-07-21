import os

def list_runs(logs_base_dir):
    runs = [d for d in os.listdir(logs_base_dir) if d.startswith('run_') and os.path.isdir(os.path.join(logs_base_dir, d))]
    runs.sort()
    return runs

def list_processes():
    return [
        ('extraction.log', 'Extraction'),
        ('transformation.log', 'Transformation'),
        ('validation_errors.log', 'Validation'),
        ('loading.log', 'Loading'),
    ]

def print_log_section(log_path, section_name):
    print(f"\n{'='*10} {section_name} {'='*10}")
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            content = f.read()
            if content.strip():
                print(content)
            else:
                print("(No logs)")
    else:
        print("(Log file not found)")

def main():
    base_dir = os.path.dirname(__file__)
    logs_base_dir = os.path.join(base_dir, 'logs')
    runs = list_runs(logs_base_dir)
    if not runs:
        print("No ETL runs found.")
        return
    print("Available ETL runs:")
    for idx, run in enumerate(runs):
        print(f"  {idx+1}. {run}")
    run_choice = input(f"Select a run (1-{len(runs)}): ")
    try:
        run_idx = int(run_choice) - 1
        if run_idx < 0 or run_idx >= len(runs):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return
    run_dir = os.path.join(logs_base_dir, runs[run_idx])
    processes = list_processes()
    print("\nAvailable processes:")
    for idx, (_, name) in enumerate(processes):
        print(f"  {idx+1}. {name}")
    print(f"  {len(processes)+1}. All")
    proc_choice = input(f"Select a process (1-{len(processes)+1}): ")
    try:
        proc_idx = int(proc_choice) - 1
        if proc_idx < 0 or proc_idx > len(processes):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return
    if proc_idx == len(processes):
        # All
        for log_file, name in processes:
            print_log_section(os.path.join(run_dir, log_file), name)
    else:
        log_file, name = processes[proc_idx]
        print_log_section(os.path.join(run_dir, log_file), name)

if __name__ == "__main__":
    main() 