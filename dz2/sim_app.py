import random
import RTOS as rt
import statistics as st
def print_stream(stream: list) -> None:
    output = ""
    for task in stream:
        output += f"{task}\n"
    print(output)
def generate_task_stream(
        cycle_q: int,
        periodic_q: int,
        impulse_q: int,
        max_instruction_size: int = 64,
        max_time_cycle: int = 60,
        max_time_periodic: int = 100,
        max_time_impulse: int = 20,
        ttl_cycle: int = 50,
        ttl_periodic: int = 95,
        ttl_impulse: int = 10,
) -> list:
    cycle_list = []
    for i in range(cycle_q):
        generated_exec_time = random.randint(1, max_time_cycle)
        generated_n_instructions = random.randint(1, 100)
        generated_size_bits = generated_n_instructions * max_instruction_size
        generated_task = rt.Task(task_id=i, execution_time=generated_exec_time, size_bits=generated_size_bits, task_type="CYCLE_TASK", ttl=ttl_cycle)
        cycle_list.append(generated_task)
    periodic_list = []
    for i in range(periodic_q):
        generated_exec_time = random.randint(1, max_time_periodic)
        generated_n_instructions = random.randint(1, 100)
        generated_size_bits = generated_n_instructions * max_instruction_size
        generated_task = rt.Task(task_id=i + cycle_q, execution_time=generated_exec_time, size_bits=generated_size_bits, task_type="PERIODIC_TASK", ttl=ttl_periodic)
        periodic_list.append(generated_task)
    impulse_list = []
    for i in range(impulse_q):
        generated_exec_time = random.randint(1, max_time_impulse)
        generated_n_instructions = random.randint(1, 100)
        generated_size_bits = generated_n_instructions * max_instruction_size
        generated_task = rt.Task(task_id=i + cycle_q + periodic_q, execution_time=generated_exec_time, size_bits=generated_size_bits, task_type="IMPULSE_TASK", ttl=ttl_impulse)
        impulse_list.append(generated_task)
    out = cycle_list + periodic_list + impulse_list
    random.shuffle(out)
    return out

if __name__ == '__main__':
    print("Введите количество задач типа CYCLE_TASK, PERIODIC_TASK, IMPULSE_TASK через пробел")
    user_input = input()
    user_input = user_input.split(" ")
    if len(user_input) != 3:
        print("Введены некорректные данные")
        exit(0)
    try:
        q_tasks = [int(item) for item in user_input]
    except ValueError:
        print("Введены некорректные данные")
        exit(0)
    n_proc = 4
    proc_freq = 1 * 10**9
    interrupt_on = 4
    task_memory = None
    n_tasks = sum(q_tasks)
    print(f"Текущие параметры модели: кол-во процессоров - {n_proc}, частота - {proc_freq} Гц, количество задач: {n_tasks}, квант времени: {interrupt_on}")
    print("Синтаксис:\n-генерация: генерация потока с параметрами по-умолчанию\n-старт: начало симуляции с параметарами по-умолчанию\n-генерация-доп: генерация с измененными параметрами\n-старт-доп: начало симуляции с измененными параметрами\n-выход: выход из программы\n-старт-8: симуляция с параметрами по-умолчанию, но кол-вом процессоров - 8.")
    while True:
        command = input()
        if command == "-генерация":
            task_memory = rt.Memory()
            stream = generate_task_stream(q_tasks[0], q_tasks[1], q_tasks[2])
            for i in range(n_tasks):
                task_memory.add(stream[i], i)
            print(f"Сгенерирован поток из {n_tasks} задач: ")
            print_stream(stream)
            continue
        elif command == "-старт":
            if task_memory is None:
                print("Поток не сгенерирован. Сгенерируйте поток.")
                continue
            rtos = rt.RTOS(n_proc, proc_freq, interrupt_on, task_memory)
            rt.clear_streams(rtos.processors)
            print(rtos.ethernet)
            distrib_count = rtos.launch_round_robin()
            print(f"Ожидаемое значение распределения: {st.count_avg(distrib_count)}")
            print(f"Среднее отклонение: {st.count_stdev(distrib_count)}")
            print(f"Относительное среднее отклонение {(st.count_stdev(distrib_count) / st.count_avg(distrib_count)) * 100}%")
            st.draw_bar(distrib_count)
            exit(0)
        elif command == "-генерация-доп":
            task_memory = rt.Memory()
            print("Введите параметры генератора через пробел:\nмаксимальное кол-во тактов CYCLE_TASK,\nмаксимальное кол-во тактов PERIODIC_TASK,\nмаксимальное кол-во тактов IMPULSE_TASK\nTTL CYCLE_TASK,\nTTL PERIODIC_TASK\nTTL IMPULSE_TASK")
            user_input = input()
            user_input = user_input.split(" ")
            if len(user_input) != 6:
                print("Введены некорректные данные")
                continue
            try:
                params = [int(item) for item in user_input]
            except ValueError:
                print("Введены некорректные данные")
                continue
            stream = generate_task_stream(q_tasks[0], q_tasks[1], q_tasks[2], params[0], params[1], params[2], params[3], params[4], params[5])
            for i in range(n_tasks):
                task_memory.add(stream[i], i)
            print(f"Сгенерирован поток из {n_tasks} задач: ")
            print_stream(stream)
            continue
        elif command == "-старт-доп":
            if task_memory is None:
                print("Поток не сгенерирован. Сгенерируйте поток.")
            print(f"Текущие параметры модели: кол-во процессоров - {n_proc}, частота - {proc_freq} Гц, квант времени: {interrupt_on}")
            print("Введите параметры модели через пробел: кол-во процессоров, частота, квант времени")
            user_input = input()
            user_input = user_input.split(" ")
            if len(user_input) != 3:
                print("Введены некорректные данные")
                continue
            try:
                params = [int(item) for item in user_input]
            except ValueError:
                print("Введены некорректные данные")
                continue
            print(f"Текущие параметры модели: кол-во процессоров - {params[0]}, частота - {params[1]} Гц, квант времени: {params[2]}")
            rtos = rt.RTOS(params[0], params[1], params[2], task_memory)
            rt.clear_streams(rtos.processors)
            print(rtos.ethernet)
            distrib_count = rtos.launch_round_robin()
            print(f"Ожидаемое значение распределения: {st.count_avg(distrib_count)}")
            print(f"Среднее отклонение: {st.count_stdev(distrib_count)}")
            print(f"Относительное среднее отклонение {(st.count_stdev(distrib_count)/st.count_avg(distrib_count))*100}%")
            st.draw_bar(distrib_count)
            exit(0)
        elif command == "-выход":
            exit(0)
        elif command == "-старт-8":
            if task_memory is None:
                print("Поток не сгенерирован. Сгенерируйте поток.")
                continue
            rtos = rt.RTOS(8, proc_freq, interrupt_on, task_memory)
            rt.clear_streams(rtos.processors)
            print(rtos.ethernet)
            distrib_count = rtos.launch_round_robin()
            print(f"Ожидаемое значение распределения: {st.count_avg(distrib_count)}")
            print(f"Среднее отклонение: {st.count_stdev(distrib_count)}")
            print(f"Относительное среднее отклонение {(st.count_stdev(distrib_count) / st.count_avg(distrib_count)) * 100}%")
            st.draw_bar(distrib_count)
            exit(0)
        else:
            print("Команда не распознана")
            continue
