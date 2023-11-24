import numpy as np
from tqdm.notebook import tqdm


class DisChannel:
    def __init__(self, pbOff=False, leave=True):
        self.__numb = None
        self.__arraySize = None
        self.__progBarOff = pbOff  # Отключить прогресс бар.
        self.__leave = leave  # Удалять прогресс бар после выполнения.

    def modelChannel(self, array: np.ndarray, probability: float) -> np.ndarray:
        """
            Модель канала с ошибками.
            Probability: float - вероятность ошибки от 0.00 до 1.00 иначе ValueError.
        """
        if probability < 0 or probability > 1:
            raise ValueError

        self.__numb = 0
        self.__arraySize = array.size

        # \033[41m - красный.
        # \033[49m - по умолчанию.
        for i in tqdm(range(array.shape[0]),
                      desc="Передача битов через канал",
                      disable=self.__progBarOff,
                      leave=self.__leave):

            for j in range(14):
                if probability > np.random.uniform(0, 1):
                    array[i][j] = int(not array[i][j])
                    self.__numb += 1

        return array

    def getNumb(self):
        return {
            "ErrorBite": self.__numb,
            "AllBite": self.__arraySize,
            "probabilityError": self.__numb / self.__arraySize
        }
