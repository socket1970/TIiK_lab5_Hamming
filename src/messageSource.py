import numpy as np
from tqdm.notebook import tqdm

from math import ceil


class BMSM:
    # Binary Message Source Model

    def __init__(self, pbOff=False, leave=True):
        self.__quantityBite = None
        self.__zero = None
        self.__progBarOff = pbOff  # Отключить прогресс бар.
        self.__leave = leave  # Удалять прогресс бар после выполнения.

    def getRandBytes(self, n: int, probability: float) -> np.ndarray:
        """
            Генерация n битов с вероятностью нуля probability.
        """
        if probability < 0 or probability > 1:
            raise ValueError

        n = ceil(n / 8)

        new_arr = np.array([np.random.choice([0, 1], size=8, p=[probability, 1-probability])
                            for _ in tqdm(range(n), desc="Генерация битов", disable=self.__progBarOff, leave=self.__leave)])

        self.__quantityBite = new_arr.size
        self.__zero = np.count_nonzero(new_arr == 0)

        return new_arr

    def getNumb(self):
        return {
            "quantityBite": self.__quantityBite,
            "zero": self.__zero,
            "probabilityZero": self.__zero / self.__quantityBite
        }
