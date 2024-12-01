import random


class Task:  # Объект, содержащий информацию об одной задаче для исполнения
    def __init__(self, task_id: int, execution_time: int):
        self.task_id = task_id  # Уникальное число, чтобы идентифицировать задачу
        self.execution_time = execution_time  # Время выполнения задачи в тактах
        self.remaining_time = self.execution_time  # Задача хранит сколько осталось тактов до её выполнения
        self.cycle = 0  # Задача хранит сколько раз она была отправлена в ожидание процессором

    def run(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1  # Уменьшаем количество тактов для завершения по вызову run()

    @staticmethod
    def generate_random_tasks(n: int) -> list:  # Генерация случайных задач, для удобства
        generated_tasks = []
        for i in range(n):
            generated_exec_time = random.randint(1, 100)
            generated_task = Task(task_id=i, execution_time=generated_exec_time)
            generated_tasks.append(generated_task)
        return generated_tasks

    def __str__(self):
        return f'Task ID: {self.task_id}, Execution Time: {self.execution_time}'  # Для удобства вывода объектов класса Task


class Memory:  # Класс, играющий роль карты памяти для хранения задач
    def __init__(self):
        self.memory = {}

    def add(self, task: Task, address: int):  # Добавление задачи в память
        self.memory[address] = task

    def get(self, address: int):  # Получение задачи из памяти
        return self.memory[address]

    def delete(self, address: int):  # Удаление задачи из памяти
        del self.memory[address]


class Processor:
    def __init__(self, processor_id: int, frequency: int, interrupt_on: int):
        self.processor_id = processor_id
        self.frequency = frequency
        self.interrupt_on = interrupt_on
        self.total_time_spent = 0

    def __hash__(self):
        return hash(self.processor_id)

    def __eq__(self, other):
        return self.processor_id == other.processor_id

    def execute(self, task: Task):
        time_spent = 0
        for i in range(self.interrupt_on):
            if task.remaining_time > 0:
                time_spent += 1
                task.run()
                if task.remaining_time <= 0:
                    print(f"Задача {task.task_id} выполнена на процессоре {self.processor_id}, время: {self.total_time_spent / self.frequency} с.")
                    break
        if task.remaining_time > 0:
            print(f"Задача {task.task_id} отправлена в ожидание процессором {self.processor_id}, кол-во пройденных кругов: {task.cycle}, время {self.total_time_spent / self.frequency} с.")
            task.cycle += 1
        self.total_time_spent += time_spent


class RTOS:
    def __init__(self, n_processors: int, frequency: int, interrupt_on: int, task_memory: Memory):
        self.processors = []
        for i in range(n_processors):
            self.processors.append(Processor(i, frequency, interrupt_on))
        self.tasks = []
        for key in task_memory.memory.keys():
            self.tasks.append(task_memory.get(key))
    @staticmethod
    def is_sequence_executed(tasks: list) -> bool:
        for task in tasks:
            if task.remaining_time > 0:
                return False
        return True
    def launch_round_robin(self):
        n_processors = len(self.processors)
        n_tasks = len(self.tasks)
        tasks_distribution = {}
        for i in range(n_processors):
            tasks_distribution[self.processors[i]] = []
        for i in range(n_tasks):
            task = self.tasks[i]
            tasks_distribution = dict(sorted(tasks_distribution.items(), key=lambda item: len(item[1]), reverse=False))
            least_loaded_processor = list(tasks_distribution.keys())[0]
            tasks_distribution[least_loaded_processor].append(task)
            print(f"Задача с id {task.task_id} была присвоена процессору {least_loaded_processor.processor_id}")
            for key in tasks_distribution.keys():
                for task in tasks_distribution[key]:
                    key.execute(task)

        print("Задачи прочитаны из памяти")

        tasks_distribution_remaining = {}

        for key in tasks_distribution.keys():
            tasks_distribution_remaining[key] = [task for task in tasks_distribution[key] if task.remaining_time > 0]

        for key in tasks_distribution_remaining.keys():
            is_done = RTOS.is_sequence_executed(tasks_distribution_remaining[key])
            while not is_done:
                for task in tasks_distribution_remaining[key]:
                    key.execute(task)
                is_done = RTOS.is_sequence_executed(tasks_distribution_remaining[key])



        for key in tasks_distribution.keys():
            print(f"Процессор {key.processor_id} завершил свою работу с {len(tasks_distribution[key])} задачами за {key.total_time_spent / key.frequency} с.")



if __name__ == '__main__':
    n_processors = 4
    frequency = 2.5 * 10**6
    interrupt_on = 4
    task_memory = Memory()
    rand_tasks = Task.generate_random_tasks(5)
    for task in rand_tasks:
        print(f"Запланирована задача с id {task.task_id} и продолжительностью {task.execution_time} тактов")
    for i in range(5):
        task_memory.add(rand_tasks[i], i)
    rtos = RTOS(n_processors, frequency, interrupt_on, task_memory)
    rtos.launch_round_robin()


























