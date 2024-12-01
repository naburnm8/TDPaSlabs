import random


class Task:
    def __init__(self,task_id: int, execution_time: int):
        self.task_id = task_id
        self.execution_time = execution_time
        self.remaining_time = self.execution_time
        self.cycle = 0

    def run(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1

    @staticmethod
    def generate_random_tasks(n: int) -> list:
        generated_tasks = []
        for i in range(n):
            generated_exec_time = random.randint(1, 100)
            generated_task = Task(task_id=i, execution_time=generated_exec_time)
            generated_tasks.append(generated_task)
        return generated_tasks


class Memory:
    def __init__(self):
        self.memory = {}

    def add(self, task: Task, address: int):
        self.memory[address] = task

    def get(self, address: int):
        return self.memory[address]

    def delete(self, address: int):
        del self.memory[address]


class Processor:
    def __init__(self, processor_id: int, frequency: int, interrupt_on: int):
        self.processor_id = processor_id
        self.frequency = frequency
        self.interrupt_on = interrupt_on

    def execute(self, task: Task):
        time_spent = 0
        for i in range(self.interrupt_on):
            if task.remaining_time > 0:
                time_spent += 1
                task.run()