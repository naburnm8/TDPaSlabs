import random



class Task:  # Объект, содержащий информацию об одной задаче для исполнения
    def __init__(self, task_id: int, execution_time: int, size_bits: int = 64):
        self.task_id = task_id  # Уникальное число, чтобы идентифицировать задачу
        self.execution_time = execution_time  # Время выполнения задачи в тактах
        self.remaining_time = self.execution_time  # Задача хранит сколько осталось тактов до её выполнения
        self.cycle = 0  # Задача хранит сколько раз она была отправлена в ожидание процессором
        self.size_bits = size_bits  # Размер задачи в битах

    def run(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1  # Уменьшаем количество тактов для завершения по вызову run()

    @staticmethod
    def generate_random_tasks(n: int, max_instrucion_size: int = 64) -> list:  # Генерация случайных задач, для удобства
        generated_tasks = []
        for i in range(n):
            generated_exec_time = random.randint(1, 100)
            generated_n_instructions = random.randint(1, 100)
            generated_size_bits = generated_n_instructions * max_instrucion_size
            generated_task = Task(task_id=i, execution_time=generated_exec_time, size_bits=generated_size_bits)
            generated_tasks.append(generated_task)
        return generated_tasks

    def __str__(self):
        return f'ID задачи: {self.task_id}, время выполнения: {self.execution_time}'  # Для удобства вывода объектов класса Task


class Frame:  # Класс, являющийся моделью кадра по стандарту IEEE P802.3ba™/D0.9
    def __init__(self, max_size: int = 12144, headers_size: int = 144, min_size: int = 512):  # Максимальные размеры кадра и размер заголовков из стандарта
        self.max_size = max_size
        self.headers_size = headers_size
        self.payload_max_size = max_size - headers_size  # В соответствии с логикой деления на кадры, задаем максимальный размер посылки
        self.payload = []  # Храним посылку, это список задач.
        self.min_size = min_size

    @staticmethod
    def count_payload(payload: list) -> int:  # Метод, считающий текущий размер посылки
        payload_size = 0
        for task in payload:
            payload_size = payload_size + task.size_bits
        return payload_size
    def add_payload(self, payload: Task) -> bool:  # Добавляем задачу в посылку только если вместе с ней размер не перевалит за максимальное
        if Frame.count_payload(self.payload) + payload.size_bits < self.payload_max_size:
            self.payload.append(payload)
            return True  # Возвращаем True если добавили
        return False  # иначе, False.

    def get_size(self) -> int:
        if Frame.count_payload(self.payload) + self.headers_size < self.min_size:
            return self.min_size
        return Frame.count_payload(self.payload) + self.headers_size
    def __str__(self): # Для удобства вывода объектов класса
        tasks_text = ""
        for task in self.payload:
            tasks_text += f"{task.task_id}: {task.size_bits}; "
        output = "Кадр {" + tasks_text + "} " + Frame.count_payload(self.payload).__str__()
        return output


class IEEE100GBIT:  # Класс, являющийся моделью канала связи по стандарту IEEE P802.3ba™/D0.9
    @staticmethod
    def distribute_tasks(tasks: list) -> list:  # Распределяем задачи по кадрам в соответствии с описанным принципом
        frames = []
        this_frame = Frame()
        for task in tasks:
            if not this_frame.add_payload(task):  # Если получаем False при добавлении в посылку, добавляем этот кадр в список кадров и добавляем задачу к новому.
                frames.append(this_frame)
                this_frame = Frame()
                this_frame.add_payload(task)
        frames.append(this_frame)
        return frames
    def __init__(self, tasks: list, data_rate: int = 100 * 10**9):
        self.frames = IEEE100GBIT.distribute_tasks(tasks)  # Распределяем задачи по кадрам
        self.data_rate = data_rate  # Используем скорость передачи из стандарта
    def count_transmission_time(self) -> float:
        total_bits_size = 0
        for frame in self.frames:
            total_bits_size += frame.get_size()  # Подсчитываем в сумму размер каждого из кадров из разделения
        return total_bits_size / self.data_rate  # и возвращаем время передачи путём деления на скорость передачи

    def __str__(self):  # Для удобства вывода объектов класса
        output = ""
        for i in range(len(self.frames)):
            output += f"{i + 1}: {self.frames[i]};\n"
        return output


class Memory:  # Класс, играющий роль карты памяти для хранения задачи
    def __init__(self):
        self.memory = {}

    def add(self, task: Task, address: int):  # Добавление задачи в память
        self.memory[address] = task

    def get(self, address: int):  # Получение задачи из памяти
        return self.memory[address]

    def delete(self, address: int):  # Удаление задачи из памяти
        del self.memory[address]

def print_to_processor_stream(processor_id: int, msg: str) -> None:
    with open(f"proc{processor_id}result.txt", "a", encoding="utf-8") as file:
        file.write(msg)

class Processor:  # Класс, играющий роль процессора, исполняющего задачи
    def __init__(self, processor_id: int, frequency: int, interrupt_on: int, start_time: float = 0, n_cores: int = 8):
        self.processor_id = processor_id  # Уникальный идентификатор
        self.frequency = frequency  # Частота процессора, для перевода тактов в секунды
        self.interrupt_on = interrupt_on  # Количество тактов, выделенных под одну задачу
        self.total_time_spent = 0  # Процессор хранит сколько всего тактов он проработал
        self.n_cores = n_cores # Процессор хранит количество ядер
        self.start_time = start_time

    def __hash__(self):
        return hash(self.processor_id)  # Для использования объектов этого класса в словарях в качестве ключей

    def __eq__(self, other):
        return self.processor_id == other.processor_id  # Для использования объектов этого класса в словарях в качестве ключей

    def execute(self, task: Task):  # Метод для исполнения задачи до прерывания
        time_spent = 0  # Учет затраченных тактов на задачу
        for i in range(self.interrupt_on * self.n_cores):  # Исполняем столько тактов, сколько можно до прерывания
            if task.remaining_time > 0:  # Заходим в тело только если задача не была уже выполнена
                time_spent += 1
                task.run()
                if task.remaining_time <= 0:
                    print_to_processor_stream(self.processor_id, f"Задача {task.task_id} выполнена на процессоре {self.processor_id}, время: {(self.total_time_spent / self.frequency) + self.start_time} с.\n")
                    break
        if task.remaining_time > 0:
            print_to_processor_stream(self.processor_id, f"Задача {task.task_id} отправлена в ожидание процессором {self.processor_id}, кол-во периодов ожидания: {task.cycle}, время {(self.total_time_spent / self.frequency) + self.start_time} с.\n")
            task.cycle += 1
        self.total_time_spent += time_spent  # Учет затраченных тактов


class RTOS:  # Класс, реализующий логику пересылки задач планировщиком Round-Robin
    def __init__(self, n_processors: int, frequency: int, interrupt_on: int, task_memory: Memory):
        self.tasks = []
        for key in task_memory.memory.keys():
            self.tasks.append(task_memory.get(key))  # Формируем список задач на исполнение
        self.ethernet = IEEE100GBIT(self.tasks)  # Формируем список кадров в соответствии с описанной логикой
        self.time_of_transfer = self.ethernet.count_transmission_time()  # Время передачи кадров по каналу связи
        self.processors = []
        for i in range(n_processors):
            self.processors.append(Processor(i, frequency, interrupt_on, self.time_of_transfer)) # Формируем список процессоров, которые будут обрабатывать задачи


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
        tasks_distribution_count = {}
        for i in range(n_processors):
            tasks_distribution[self.processors[i]] = [] # Для хранения присвоенных задач используем словарь списков
            tasks_distribution_count[self.processors[i]] = 0 # Храним количество задач
        for i in range(n_tasks):
            task = self.tasks[i]  # Следующая задача из памяти
            tasks_distribution = dict(sorted(tasks_distribution.items(), key=lambda item: len(item[1]), reverse=False))  # Ищем наименее загруженный процессор
            least_loaded_processor = list(tasks_distribution.keys())[0]
            tasks_distribution[least_loaded_processor].append(task) # Пересылаем задачу к наименее загруженному процессору
            tasks_distribution_count[least_loaded_processor] += 1
            print(f"Задача с id {task.task_id} была переслана процессору {least_loaded_processor.processor_id}")
            for key in tasks_distribution.keys():
                for task in tasks_distribution[key]:
                    key.execute(task)  # После присваивания исполняем задачи
                tasks_distribution[key] = [task for task in tasks_distribution[key] if task.remaining_time > 0] # Очищаем исполненные задачи

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
            print(f"Процессор {key.processor_id} завершил свою работу с {tasks_distribution_count[key]} задачами за {(key.total_time_spent / key.frequency) + self.time_of_transfer} с.")
            print_to_processor_stream(key.processor_id, f"КОНЕЦ ФАЙЛА")

def clear_streams(processors: list) -> None:
    for processor in processors:
        with open(f"proc{processor.processor_id}result.txt", "w", encoding="utf-8") as file:
            file.write("")

if __name__ == '__main__':
    n_processors = 4
    frequency = 1 * 10**9  # Тактовая частота нашего процессора
    interrupt_on = 4
    task_memory = Memory()
    n_tasks = 1000
    rand_tasks = Task.generate_random_tasks(n_tasks)
    for task in rand_tasks:
        print(f"Запланирована задача с id {task.task_id} и продолжительностью {task.execution_time} тактов")
    for i in range(n_tasks):
        task_memory.add(rand_tasks[i], i)
    rtos = RTOS(n_processors, frequency, interrupt_on, task_memory)
    clear_streams(rtos.processors)
    print(rtos.ethernet)
    rtos.launch_round_robin()




























