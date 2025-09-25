# src/simulator.py
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from typing import Optional

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0
    remaining: int = field(init=False)
    start_time: Optional[int] = None
    completion_time: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.burst

# ---------- CPU Scheduling Algorithms ----------
def fcfs_schedule(processes: List[Process]):
    procs = sorted([Process(p.pid, p.arrival, p.burst, p.priority) for p in processes], key=lambda p: p.arrival)
    timeline = []
    time = 0
    for p in procs:
        if time < p.arrival:
            time = p.arrival
        start = time
        end = start + p.burst
        p.start_time = start
        p.completion_time = end
        timeline.append((p.pid, start, end))
        time = end
    return timeline, {p.pid: p for p in procs}

def rr_schedule(processes: List[Process], quantum: int):
    from collections import deque
    procs = sorted([Process(p.pid, p.arrival, p.burst, p.priority) for p in processes], key=lambda p: p.arrival)
    q = deque()
    timeline = []
    time = 0
    i = 0
    while i < len(procs) or q:
        while i < len(procs) and procs[i].arrival <= time:
            q.append(procs[i])
            i += 1
        if not q:
            time = procs[i].arrival
            continue
        p = q.popleft()
        if p.start_time is None:
            p.start_time = time
        run = min(quantum, p.remaining)
        timeline.append((p.pid, time, time + run))
        p.remaining -= run
        time += run
        while i < len(procs) and procs[i].arrival <= time:
            q.append(procs[i])
            i += 1
        if p.remaining > 0:
            q.append(p)
        else:
            p.completion_time = time
    return timeline, {p.pid: p for p in procs}

def sjf_schedule(processes: List[Process], preemptive=False):
    procs = sorted([Process(p.pid, p.arrival, p.burst, p.priority) for p in processes], key=lambda p: p.arrival)
    time = 0
    done, timeline, ready, i = [], [], [], 0
    while len(done) < len(procs):
        while i < len(procs) and procs[i].arrival <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i].arrival
            continue
        if preemptive:
            ready.sort(key=lambda p: (p.remaining, p.arrival))
            p = ready[0]
            if p.start_time is None:
                p.start_time = time
            timeline.append((p.pid, time, time + 1))
            p.remaining -= 1
            time += 1
            if p.remaining == 0:
                p.completion_time = time
                done.append(p)
                ready.remove(p)
        else:
            ready.sort(key=lambda p: (p.burst, p.arrival))
            p = ready.pop(0)
            if p.start_time is None:
                p.start_time = time
            timeline.append((p.pid, time, time + p.burst))
            time += p.burst
            p.completion_time = time
            done.append(p)
    return timeline, {p.pid: p for p in procs}

def priority_schedule(processes: List[Process], preemptive=False):
    procs = sorted([Process(p.pid, p.arrival, p.burst, p.priority) for p in processes], key=lambda p: p.arrival)
    time, done, timeline, ready, i = 0, [], [], [], 0
    while len(done) < len(procs):
        while i < len(procs) and procs[i].arrival <= time:
            ready.append(procs[i])
            i += 1
        if not ready:
            time = procs[i].arrival
            continue
        ready.sort(key=lambda p: (p.priority, p.arrival))
        p = ready[0]
        if preemptive:
            if p.start_time is None:
                p.start_time = time
            timeline.append((p.pid, time, time + 1))
            p.remaining -= 1
            time += 1
            if p.remaining == 0:
                p.completion_time = time
                done.append(p)
                ready.remove(p)
        else:
            if p.start_time is None:
                p.start_time = time
            timeline.append((p.pid, time, time + p.burst))
            time += p.burst
            p.completion_time = time
            done.append(p)
            ready.remove(p)
    return timeline, {p.pid: p for p in procs}

# ---------- Metrics ----------
def compute_metrics(proc_map: Dict[str, Process]):
    out = {}
    total_wait, total_turn = 0, 0
    for pid, p in proc_map.items():
        turnaround = p.completion_time - p.arrival
        waiting = turnaround - p.burst
        out[pid] = {'arrival': p.arrival, 'burst': p.burst, 'completion': p.completion_time,
                    'turnaround': turnaround, 'waiting': waiting}
        total_wait += waiting
        total_turn += turnaround
    n = len(proc_map)
    out['averages'] = {'avg_waiting': total_wait/n, 'avg_turnaround': total_turn/n}
    return out

# ---------- Gantt Chart ----------
def plot_gantt(timeline: List[Tuple[str,int,int]], title='Gantt Chart', filepath=None):
    labels, starts, durations = [], [], []
    for pid, s, e in timeline:
        labels.append(pid)
        starts.append(s)
        durations.append(e-s)
    fig, ax = plt.subplots(figsize=(10, 0.8*len(timeline)+2))
    ax.barh(range(len(timeline)), durations, left=starts, height=0.6, color="skyblue", edgecolor="black")
    ax.set_yticks(range(len(timeline)))
    ax.set_yticklabels([f"{pid} ({s}->{s+d})" for pid, s, d in zip(labels, starts, durations)])
    ax.set_xlabel("Time")
    ax.set_title(title)
    plt.tight_layout()
    if filepath:
        plt.savefig(filepath)
    else:
        plt.show()
    plt.close()
