from src.messageSource import *
from src.hammingCode import *
from src.discreteChannel import *

from scipy import stats
from prettytable import PrettyTable
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm


class Model:
    def __init__(self, bite: int, probabilityError: str, probabilityZero=0.5, pdGeneralOff=False, pbOff=True,
                 leave=True, write_to_csv=True, name_csv_file="отчет"):
        self.__bite = bite
        self.__probabilityError = probabilityError.split(" ")
        self.__probabilityZero = probabilityZero
        self.__pbOff = pbOff  # Выключить прогресс бар каждого шага.
        self.__pdGeneralOff = pdGeneralOff  # Выключить общий прогресс бар.
        self.__leave = leave  # Удалять прогресс бар после выполнения.
        self.__write_to_csv = write_to_csv  # Запись в csv таблицу
        self.__name_csv_file = name_csv_file

    def start(self):
        bmsm = BMSM(pbOff=self.__pbOff, leave=self.__leave)
        code = HamCode(pbOff=self.__pbOff, leave=self.__leave)
        channel = DisChannel(pbOff=self.__pbOff, leave=self.__leave)

        numb = int(self.__probabilityError[-1])

        ans = {
            "quantityBite": [],  # сколько битов сгенерировано.
            "quantityBiteChannel": [],  # сколько битов прошло через канал.
            "quantityZero": [],  # сколько нулей сгенерировано.

            "probabilityError": [],  # заданная вероятность ошибки в канале.
            "realProbabilityError": [],  # рассчитанная вероятность ошибки в канале.

            "probabilityZero": [],  # заданная вероятность нуля.
            "realProbabilityZero": [],  # рассчитанная вероятность нуля.

            "byteError": []  # сколько ошибок отловил код Хэмминга.
        }

        for probabilityError in self.__probabilityError[:len(self.__probabilityError) - 1]:
            probabilityError = float(probabilityError)
            dov = []  # доверительный интервал ошибки в канале.
            zero = []  # доверительный интервал вероятности нуля.
            for _ in tqdm(range(numb), desc=f"{probabilityError}", disable=self.__pdGeneralOff):
                array = bmsm.getRandBytes(n=self.__bite, probability=self.__probabilityZero)
                encode = code.encode(array)
                c = channel.modelChannel(encode, probabilityError)
                code.decode(c)

                dov.append(channel.getNumb()["probabilityError"])
                zero.append(bmsm.getNumb()["probabilityZero"])

            ans["quantityBite"].append('{0:,}'.format(bmsm.getNumb()["quantityBite"]).replace(',', '.'))
            ans["quantityBiteChannel"].append(channel.getNumb()["AllBite"])
            ans["quantityZero"].append(bmsm.getNumb()["zero"])

            ans["probabilityError"].append(probabilityError)
            ans["realProbabilityError"].append(self.__confidence_interval(dov))

            ans["probabilityZero"].append(self.__probabilityZero)
            ans["realProbabilityZero"].append(self.__confidence_interval(zero))
        print()

        self.__getTable(ans)
        self.__getPlot(ans)

    def __getPlot(self, data):
        pk1 = self.__pK_hard(data["probabilityError"])
        pk2 = self.__pK_easy(data["probabilityError"])
        p = data["probabilityError"]

        plt.loglog(p, pk1, "go-", label='Pk*')
        plt.loglog(p, pk2, "bx-", label='Pk')

        plt.title("Код Хэмминга")
        plt.grid(True, which="both", ls="-")
        plt.xlabel("p")
        plt.ylabel("Pk(*)")
        plt.legend()

        plt.show()

    def __getTable(self, data):
        pt = PrettyTable()

        pt.add_column("p", data["probabilityError"])  # заданная вероятность ошибки на бит.
        pt.add_column("p*", data["realProbabilityError"])
        pt.add_column("Pk*", self.__pK_hard(data["probabilityError"]))
        pt.add_column("Pk", self.__pK_easy(data["probabilityError"]))
        pt.add_column("Заданная вероятность нуля", data["probabilityZero"])
        pt.add_column("Рассчитанная вероятность нуля", data["realProbabilityZero"])
        pt.add_column("Количество битов", data["quantityBite"])

        print(pt)

        if self.__write_to_csv:
            with open(f"{self.__name_csv_file}.csv", 'w', newline='') as f_output:
                f_output.write(pt.get_csv_string())

    @staticmethod
    def __confidence_interval(array):
        n = 3  # числа после запятой.
        data = np.array(array)

        # Вычисляем среднее значение и стандартное отклонение
        mean = np.mean(data)
        std_dev = np.std(data)

        # Вычисляем доверительный интервал с уровнем доверия 90%
        confidence_interval = stats.norm.interval(0.90, loc=mean, scale=std_dev)
        return f"{round(mean, n)} ± {round(confidence_interval[1] - mean, n)}"

    @staticmethod
    def __pK_hard(arr, n=4):
        ans = []
        for i in arr:
            p = i
            ans.append(round(
                1 - (1 - p) ** 7 - 7 * p * (1 - p) ** 6,
                n))
        return ans

    @staticmethod
    def __pK_easy(arr, n=4):
        ans = []
        for i in arr:
            p = i
            ans.append(round(
                21 * p ** 2,
                n))
        return ans


# 0.010 0.025 0.040 0.055 0.07 10
