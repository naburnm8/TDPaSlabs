from collections import Counter

import matplotlib.pyplot as plt
from RTOS import IEEE100GBIT

import numpy as np
def count_avg(distribution: dict) -> float:
    tasks = list(distribution.values())
    n_proc = len(list(distribution.keys()))
    return sum(tasks) / n_proc

def count_stdev(distribution: dict) -> float:
    sq_stdev = 0
    tasks = list(distribution.values())
    avg = count_avg(distribution)
    for item in tasks:
        sq_stdev += (item - avg) ** 2
    sq_stdev /= len(tasks)
    return sq_stdev**0.5
def draw_bar(distribution: dict) -> None:
    converted_distribution = {str(proc.processor_id): value for proc, value in distribution.items()}
    processors = list(converted_distribution.keys())
    tasks = list(converted_distribution.values())
    plt.bar(processors, tasks, color='blue')
    line_height = count_avg(distribution)
    plt.axhline(line_height, color='red', linestyle='--', linewidth=2, label='Ожидаемое кол-во задач')
    plt.title("Распределение задач по процессорам")
    plt.xlabel("ID процессора")
    plt.ylabel("Кол-во задач")
    plt.show()
def draw_ethernet_bar(ethernet: IEEE100GBIT) -> None:
    frames_occupancy = []
    for frame in ethernet.frames:
        total_frame_payload = frame.count_payload(frame.payload)
        frames_occupancy.append((total_frame_payload/12000)*100)
    indicies = []
    for i in range(len(frames_occupancy)):
        indicies.append(i)
    avg_occupancy = (sum(frames_occupancy) / len(frames_occupancy))
    plt.bar(indicies, frames_occupancy, color='blue', width=1)
    plt.axhline(avg_occupancy, color='red', linestyle='--', linewidth=2, label="Средняя заполненность")
    plt.title("Заполненность кадров ethernet в процентах")
    plt.xlabel("Номер кадра")
    plt.ylabel("Заполненность")
    plt.show()
    print(f"Средняя заполненность кадров: {avg_occupancy}%")

def draw_group_bar(tasks_distribution: dict) -> None:
    CYCLE = "CYCLE_TASK"
    PERIODIC = "PERIODIC_TASK"
    IMPULSE = "IMPULSE_TASK"

    task_types = [CYCLE, PERIODIC, IMPULSE]
    converted_distribution = {str(proc.processor_id): value for proc, value in tasks_distribution.items()}
    counts = {p: Counter(task.task_type for task in tasks) for p, tasks in converted_distribution.items()}

    x = np.arange(len(list(converted_distribution.keys())))
    width = 0.25

    fig, ax = plt.subplots()
    for i, task_type in enumerate(task_types):
        values = [counts[p].get(task_type, 0) for p in converted_distribution.keys()]
        ax.bar(x+i*width, values, width, label=task_type)

    ax.set_xlabel("Процессоры")
    ax.set_ylabel("Количество задач")
    ax.set_title("Распределение задач по процессорам")
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(list(converted_distribution.keys()))
    ax.legend(title="Типы задач")

    plt.show()

def draw_core_bar(core_distribution: dict, id_processor: int) -> None:
    converted_distribution = {str(core.core_id): value for core, value in core_distribution.items()}
    cores = list(converted_distribution.keys())
    tasks = list(converted_distribution.values())
    plt.bar(cores, tasks, color='blue')
    plt.title(f"Распределение по ядрам процессора {id_processor}")
    plt.xlabel("Номер ядра")
    plt.ylabel("Кол-во задач")
    plt.show()
def draw_all_bars(distribution: dict, ethernet: IEEE100GBIT, tasks_distrib_final: dict) -> None:
    draw_group_bar(tasks_distrib_final)
    draw_bar(distribution)
    draw_ethernet_bar(ethernet)

