import matplotlib.pyplot as plt

def count_avg(distribution: dict):
    tasks = list(distribution.values())
    n_proc = len(list(distribution.keys()))
    return sum(tasks) / n_proc

def count_stdev(distribution: dict):
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
    plt.legend()
    plt.show()
