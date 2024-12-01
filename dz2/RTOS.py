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
        return f'ID задачи: {self.task_id}, время выполнения: {self.execution_time}'  # Для удобства вывода объектов класса Task


class Memory:  # Класс, играющий роль карты памяти для хранения задач
    def __init__(self):
        self.memory = {}  # Внутри имеет структуру словаря

    def add(self, task: Task, address: int):  # Добавление задачи в память
        self.memory[address] = task

    def get(self, address: int):  # Получение задачи из памяти
        return self.memory[address]

    def delete(self, address: int):  # Удаление задачи из памяти
        del self.memory[address]


class Processor:  # Класс, играющий роль процессора, исполняющего задачи
    def __init__(self, processor_id: int, frequency: int, interrupt_on: int):
        self.processor_id = processor_id  # Уникальный идентификатор
        self.frequency = frequency  # Частота процессора, для перевода тактов в секунды
        self.interrupt_on = interrupt_on  # Количество тактов, выделенных под одну задачу
        self.total_time_spent = 0  # Процессор хранит сколько всего тактов он проработал

    def __hash__(self):
        return hash(self.processor_id)  # Для использования объектов этого класса в словарях в качестве ключей

    def __eq__(self, other):
        return self.processor_id == other.processor_id  # Для использования объектов этого класса в словарях в качестве ключей

    def execute(self, task: Task):  # Метод для исполнения задачи до прерывания
        time_spent = 0  # Учет затраченных тактов на задачу
        for i in range(self.interrupt_on):  # Исполняем столько тактов, сколько можно до прерывания
            if task.remaining_time > 0:  # Заходим в тело только если задача не была уже выполнена
                time_spent += 1
                task.run()
                if task.remaining_time <= 0:
                    print(f"Задача {task.task_id} выполнена на процессоре {self.processor_id}, время: {self.total_time_spent / self.frequency} с.")
                    break
        if task.remaining_time > 0:
            print(f"Задача {task.task_id} отправлена в ожидание процессором {self.processor_id}, кол-во периодов ожидания: {task.cycle}, время {self.total_time_spent / self.frequency} с.")
            task.cycle += 1
        self.total_time_spent += time_spent  # Учет затраченных тактов


class RTOS:  # Класс, реализующий логику пересылки задач планировщиком Round-Robin
    def __init__(self, n_processors: int, frequency: int, interrupt_on: int, task_memory: Memory):
        self.processors = []
        for i in range(n_processors):
            self.processors.append(Processor(i, frequency, interrupt_on)) # Формируем список процессоров, которые будут обрабатывать задачи
        self.tasks = []
        for key in task_memory.memory.keys():
            self.tasks.append(task_memory.get(key))  # Формируем список задач на исполнение
    @staticmethod
    def is_sequence_executed(tasks: list) -> bool:  # Проверка на то, все ли задачи в списке исполнены
        for task in tasks:
            if task.remaining_time > 0:
                return False
        return True
    def launch_round_robin(self): # Запуск исполнения задач
        n_processors = len(self.processors)
        n_tasks = len(self.tasks)
        tasks_distribution = {}
        for i in range(n_processors):
            tasks_distribution[self.processors[i]] = []  # Для хранения присвоенных задач используем словарь списков
        for i in range(n_tasks):
            task = self.tasks[i]  # Следующая задача из памяти
            tasks_distribution = dict(sorted(tasks_distribution.items(), key=lambda item: len(item[1]), reverse=False))  # Ищем наименее загруженный процессор
            least_loaded_processor = list(tasks_distribution.keys())[0]
            tasks_distribution[least_loaded_processor].append(task)  # Пересылаем задачу к наименее загруженному процессору
            print(f"Задача с id {task.task_id} была переслана процессору {least_loaded_processor.processor_id}")
            for key in tasks_distribution.keys():
                for task in tasks_distribution[key]:
                    key.execute(task)  # После присваивания исполняем задачи

        print("Задачи прочитаны из памяти")

        tasks_distribution_remaining = {}

        for key in tasks_distribution.keys():
            tasks_distribution_remaining[key] = [task for task in tasks_distribution[key] if task.remaining_time > 0]  # После прочтения задач из памяти и исполнения в прошлом цикле, остались неисполненные задачи

        for key in tasks_distribution_remaining.keys():
            is_done = RTOS.is_sequence_executed(tasks_distribution_remaining[key])  # Исполняем все задачи всех процессоров пока они все не будут исполнены
            while not is_done:
                for task in tasks_distribution_remaining[key]:
                    key.execute(task)
                is_done = RTOS.is_sequence_executed(tasks_distribution_remaining[key])



        for key in tasks_distribution.keys():
            print(f"Процессор {key.processor_id} завершил свою работу с {len(tasks_distribution[key])} задачами за {key.total_time_spent / key.frequency} с.")



if __name__ == '__main__':
    n_processors = 4
    frequency = 2.5 * 10**6  # Тактовая частота нашего процессора
    interrupt_on = 4
    task_memory = Memory()
    rand_tasks = Task.generate_random_tasks(5)
    for task in rand_tasks:
        print(f"Запланирована задача с id {task.task_id} и продолжительностью {task.execution_time} тактов")
    for i in range(5):
        task_memory.add(rand_tasks[i], i)
    rtos = RTOS(n_processors, frequency, interrupt_on, task_memory)
    rtos.launch_round_robin()


























