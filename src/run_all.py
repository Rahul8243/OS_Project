from simulator import *
import pandas as pd
import os

# ---------- Input ----------
def get_cpu_processes():
    n = int(input("Number of processes: "))
    processes = []
    for i in range(n):
        pid = f"P{i+1}"
        arrival = int(input(f"Arrival time for {pid}: "))
        burst = int(input(f"Burst time for {pid}: "))
        priority = int(input(f"Priority for {pid} (default 0): ") or 0)
        processes.append(Process(pid, arrival, burst, priority))
    return processes

def get_bankers_input():
    n = int(input("Number of processes: "))
    m = int(input("Number of resources: "))
    print("Enter Max matrix (n x m):")
    Max = [list(map(int, input(f"P{i+1} max: ").split())) for i in range(n)]
    print("Enter Allocation matrix (n x m):")
    Allocation = [list(map(int, input(f"P{i+1} allocation: ").split())) for i in range(n)]
    Available = list(map(int, input(f"Available resources ({m} values): ").split()))
    return n, m, Max, Allocation, Available

# ---------- CPU Algorithm Runner ----------
def run_cpu_algorithm(name, processes, quantum=None):
    os.makedirs("visuals", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    # Algorithm mapping
    if name == "FCFS":
        tl, pm = fcfs_schedule(processes)
    elif name == "SJF Non-Preemptive":
        tl, pm = sjf_schedule(processes, preemptive=False)
    elif name == "SJF Preemptive":
        tl, pm = sjf_schedule(processes, preemptive=True)
    elif name == "RR":
        tl, pm = rr_schedule(processes, quantum)
    elif name == "Priority Non-Preemptive":
        tl, pm = priority_schedule(processes, preemptive=False)
    elif name == "Priority Preemptive":
        tl, pm = priority_schedule(processes, preemptive=True)
    else:
        print("Invalid choice.")
        return

    metrics = compute_metrics(pm)
    print(f"\n=== {name} Results ===")
    for pid, data in metrics.items():
        if pid != "averages":
            print(f"{pid}: {data}")
    print("Averages:", metrics["averages"])

    # Export CSV
    df = pd.DataFrame([data for pid, data in metrics.items() if pid != "averages"])
    avg_row = {"PID":"Average", **metrics["averages"]}
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
    csv_path = f"results/{name.replace(' ','_')}_metrics.csv"
    df.to_csv(csv_path, index=False)
    print(f"Metrics saved to {csv_path}")

    # Export Gantt
    gantt_path = f"visuals/{name.replace(' ','_')}_Gantt.png"
    plot_gantt(tl, title=f"{name} Gantt Chart", filepath=gantt_path)
    print(f"Gantt chart saved to {gantt_path}")

# ---------- Banker ----------
def bankers_algorithm():
    n, m, Max, Allocation, Available = get_bankers_input()
    Need = [[Max[i][j]-Allocation[i][j] for j in range(m)] for i in range(n)]
    Finish = [False]*n
    safe_seq = []
    print("\nExecuting Banker's Algorithm...")
    while len(safe_seq) < n:
        allocated = False
        for i in range(n):
            if not Finish[i] and all(Need[i][j] <= Available[j] for j in range(m)):
                for j in range(m):
                    Available[j] += Allocation[i][j]
                Finish[i] = True
                safe_seq.append(f"P{i+1}")
                allocated = True
        if not allocated:
            print("System is NOT in safe state! Deadlock may occur.")
            return
    print("System is in SAFE state.")
    print("Safe sequence:", " -> ".join(safe_seq))

# ---------- Main Menu ----------
def main():
    while True:
        print("\n=== CPU & OS Scheduling Simulator ===")
        print("1. FCFS")
        print("2. SJF Non-Preemptive")
        print("3. SJF Preemptive")
        print("4. Round Robin")
        print("5. Priority Non-Preemptive")
        print("6. Priority Preemptive")
        print("7. Banker's Algorithm")
        print("8. Exit")
        choice = input("Enter choice (1-8): ")

        if choice == "8":
            print("Exiting Simulator. Goodbye!")
            break
        elif choice in ["1","2","3","4","5","6"]:
            processes = get_cpu_processes()
            quantum = None
            if choice == "4":
                quantum = int(input("Enter time quantum: "))
            mapping = {
                "1":"FCFS","2":"SJF Non-Preemptive","3":"SJF Preemptive",
                "4":"RR","5":"Priority Non-Preemptive","6":"Priority Preemptive"
            }
            run_cpu_algorithm(mapping[choice], processes, quantum)
        elif choice == "7":
            bankers_algorithm()
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
