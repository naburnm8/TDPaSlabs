from math import tanh
from typing import Callable


class CodingEvaluator:

    @staticmethod
    def calculate_accuracy_index(data: str, encoder: Callable[[str, bool, bool], str]) -> float:
        encoded_data = encoder(data, True, True)
        decoded_data = encoder(encoded_data, False, False)
        base_index = 10
        decrement = 10 / len(data)
        for ch1, ch2 in zip(data, decoded_data):
            if ch1 != ch2:
                base_index -= decrement
        return base_index

    @staticmethod
    def calculate_compression_index(data: str, encoder: Callable[[str, bool, bool], str], compression_index: float = 1) -> float:
        encoded_data = encoder(data, True, False)
        base_index = 5
        len_difference = len(encoded_data) - len(data)
        decrement = -5*tanh(len_difference*compression_index)
        return base_index + decrement

    def __init__(self, get_test_cases: Callable, **kwargs):
        self.test_cases = get_test_cases()
        self.algorithms = kwargs

    def evaluate(self):
        accuracy_indexes_dict = {}
        compression_indexes_dict = {}
        for key in self.algorithms.keys():
            algorithm = self.algorithms[key]
            accuracy_indexes = []
            compression_indexes = []
            for test_case in self.test_cases:
                accuracy_index = self.calculate_accuracy_index(test_case, algorithm)
                accuracy_indexes.append(accuracy_index)
                compression_index = self.calculate_compression_index(test_case, algorithm)
                compression_indexes.append(compression_index)
            accuracy_indexes_dict[key] = accuracy_indexes
            compression_indexes_dict[key] = compression_indexes

        for key in self.algorithms.keys():
            accuracy_indexes_dict[key] = sum(accuracy_indexes_dict[key]) / len(accuracy_indexes_dict[key])
            compression_indexes_dict[key] = sum(compression_indexes_dict[key]) / len(compression_indexes_dict[key])

        for key in self.algorithms.keys():
            print(f"Algorithm: {key}, accuracy index: {accuracy_indexes_dict[key]}, compression index: {compression_indexes_dict[key]}\n")

        print(f"Testing info:\n{len(self.algorithms.values())} algorithms\n{len(self.test_cases)} test cases\n")

