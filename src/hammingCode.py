import numpy as np
from tqdm.notebook import tqdm

matrix = ((1, 1, 1, 0),
          (0, 1, 1, 1),
          (1, 0, 1, 1))


class HamCode:
    def __init__(self, pbOff=False, leave=True) -> None:
        self.__count = 0
        self.__progBarOff = pbOff  # Отключить прогресс бар.
        self.__leave = leave  # Удалять прогресс бар после выполнения.

    def decode(self, array: np.ndarray) -> np.ndarray:
        """
            Дешифрование кода Хэмминга(7.4).
        """
        ans = np.empty(shape=(array.shape[0], 8), dtype=int)

        for i in tqdm(range(array.shape[0]), desc="Декодирование кода Хэмминга", disable=self.__progBarOff,
                      leave=self.__leave):
            new_array = np.hstack([array[i][:4], array[i][7:11]])
            new_array = self.__oneDecode(new_array)

            ans[i] = self.__checkBits(array[i], new_array)
        return ans

    def encode(self, array: np.ndarray) -> np.ndarray:
        """
            Шифрование кодом Хэмминга(7.4).
        """

        ans = np.empty(shape=(array.shape[0], 14), dtype=int)

        for i in tqdm(range(array.shape[0]),
                      desc="Кодирование кодом Хэмминга",
                      disable=self.__progBarOff,
                      leave=self.__leave):
            ans[i] = self.__oneDecode(array[i])
        return ans

    def __oneDecode(self, arr: np.ndarray) -> np.ndarray:
        """
            Принимает 1 байт и возвращает 14 бит по коду Хэмминга(7.4).
        """
        return np.hstack([self.__bitRate(arr[:4]),
                          self.__bitRate(arr[4:])])

    def __bitRate(self, array: np.ndarray) -> np.ndarray:
        """
            Принимает 4 бита и возвращает 7 бит.
        """
        arr = array
        for i in range(3):
            arr = np.append(arr, self.__XOR_AND(array, i))
        return arr

    @staticmethod
    def __XOR_AND(array: np.ndarray, step: int) -> int:
        """
            Принимает 4 бита и возвращает сумму по модулю два каждого элемента,
            с которым прошла конъюнкция с матрицей.
            N0^M0 XOR ... XOR N3^M3
        """
        array = np.logical_and(array, matrix[step])
        return int(np.logical_xor.reduce(array))

    def __checkBits(self, source_array, new_array) -> np.ndarray:
        """
            Проверка и исправление ошибки.
        """
        array = np.hstack([new_array[:4], new_array[7:11]])
        # Первые 4 бита.

        # Все три бита не сошлись.
        if source_array[4] != new_array[4] and source_array[5] != new_array[5] and source_array[6] != new_array[6]:
            self.__count += 1
            array[2] = int(not array[2])
        elif source_array[4] != new_array[4] and source_array[5] != new_array[5]:  # C0 и C1 не сошлись.
            self.__count += 1
            array[1] = int(not array[1])
        elif source_array[4] != new_array[4] and source_array[6] != new_array[6]:  # C0 и C2 не сошлись.
            self.__count += 1
            array[0] = int(not array[0])
        elif source_array[5] != new_array[5] and source_array[6] != new_array[6]:  # C1 и C2 не сошлись.
            self.__count += 1
            array[3] = int(not array[3])

        # Последние 4 бита.

        # Все три бита не сошлись.
        elif source_array[11] != new_array[11] and source_array[12] != new_array[12] and source_array[13] != new_array[13]:
            self.__count += 1
            array[5] = int(not array[5])
        elif source_array[11] != new_array[11] and source_array[12] != new_array[12]:  # C0 и C1 не сошлись.
            self.__count += 1
            array[4] = int(not array[4])
        elif source_array[11] != new_array[11] and source_array[13] != new_array[13]:  # C0 и C2 не сошлись.
            self.__count += 1
            array[7] = int(not array[7])
        elif source_array[12] != new_array[12] and source_array[13] != new_array[13]:  # C1 и C2 не сошлись.
            self.__count += 1
            array[6] = int(not array[6])
        else:
            pass

        return array

    def getNumber(self):
        return {
            "errorByte": self.__count
        }
