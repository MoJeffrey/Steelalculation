import copy
import multiprocessing as mp
from itertools import combinations
import sys

from time import time
from typing import List

from ProgressBar import ProgressBar

AllTask = 0
FinishTask = 0
PB: ProgressBar = None


class CuttingScheme:
    """
    切割方案
    """
    Slicing: list = None
    Waste: int = None
    SteelLength: int = None
    Complete: bool = None

    def __init__(self, SteelLength: int, Slicing: list):
        self.SteelLength = SteelLength
        self.Waste = SteelLength
        self.Slicing = Slicing.copy()

        for Num in Slicing:
            self.Waste = self.Waste - Num

        if self.Waste == 0:
            self.Complete = True
        else:
            self.Complete = False

class SteelNeed:
    Length: int = None
    Quantity: int = None

    def __init__(self, Length: int, Quantity):
        self.Length = Length
        self.Quantity = Quantity


class SteelNeedOrder:
    SteelNeedList: List[SteelNeed] = None

    def __init__(self):
        self.SteelNeedList = []

    def append(self, steelNeed: SteelNeed):
        self.SteelNeedList.append(steelNeed)

    def GetAllSteelNeedLengthList(self) -> list:
        SteelNeedLengthList = []
        for steelNeed in self.SteelNeedList:
            SteelNeedLengthList.append(steelNeed.Length)

        return SteelNeedLengthList

    def GetAllLength(self):
        AllLength = 0
        for NowSteelNeed in self.SteelNeedList:
            AllLength += NowSteelNeed.Length * NowSteelNeed.Quantity

        return AllLength

    def Print(self):
        String = ""
        for Need in self.SteelNeedList:
            String += f'【需求：{Need.Length}，数量：{Need.Quantity}】'
        print(String)

    def GetAllSteelQuantity(self) -> int:
        Quantity = 0
        for Need in self.SteelNeedList:
            Quantity += Need.Quantity
        return Quantity

    def Deduct(self, cuttingScheme: CuttingScheme) -> int:
        isDeduct = False
        Waste = 0
        for Slicing in cuttingScheme.Slicing:
            for Num in range(0, len(self.SteelNeedList)):
                if self.SteelNeedList[Num].Length == Slicing:
                    if self.SteelNeedList[Num].Quantity == 0:
                        return -1
                    else:
                        self.SteelNeedList[Num].Quantity -= 1
                        isDeduct = True
        if isDeduct:
            return Waste
        return -1

    def isFinish(self):
        for steelNeed in self.SteelNeedList:
            if steelNeed.Quantity != 0:
                return False
        return True


class CuttingSchemeManage:
    """
    切割方案管理
    """
    Order: SteelNeedOrder = None
    CuttingSchemeList: List[CuttingScheme] = None
    SteelLengthList: List[int] = None
    ComposeList: list = None
    HaveComplete: bool = None

    def __init__(self, order: SteelNeedOrder, SteelLengthList: List[int], CuttingSchemeList: List[CuttingScheme] = None):
        self.Order = order
        self.SteelLengthList = SteelLengthList
        self.ComposeList = []
        self.CuttingSchemeList = []
        self.HaveComplete = False

        if CuttingSchemeList is not None:
            self.CuttingSchemeList = CuttingSchemeList
            return

        for SteelLength in list(set(SteelLengthList)):
            self.ComposeList.clear()
            self.__AddSlicing(SteelLength, SteelLength, [], self.Order.GetAllSteelNeedLengthList())
        self.soft()

    def __AddSlicing(self, OriginalSteelLength: int, NowSteelLength: int, NowSlicing: list, NeedList: list):
        def append():
            TheNowSlicing.append(NeedLength)
            TheNowSlicing.sort()
            if TheNowSlicing not in self.ComposeList:
                self.ComposeList.append(TheNowSlicing)
                CS = CuttingScheme(OriginalSteelLength, TheNowSlicing)
                self.CuttingSchemeList.append(CS)

                if CS.Complete:
                    self.HaveComplete = True

        for NeedLength in NeedList:
            TheNowSlicing = NowSlicing.copy()
            if NowSteelLength > NeedLength:
                append()
                self.__AddSlicing(OriginalSteelLength, NowSteelLength - NeedLength, TheNowSlicing.copy(), NeedList)
            elif NeedLength == NowSteelLength:
                append()

    def GetCuttingSchemeList(self) -> List[CuttingScheme]:
        return self.CuttingSchemeList

    def soft(self):
        SlicingList = {}
        WasteList = []
        for CS in self.CuttingSchemeList:
            SlicingList[CS.Waste] = CS
            WasteList.append(CS.Waste)

        WasteList.sort()
        self.CuttingSchemeList = []
        for Waste in WasteList:
            self.CuttingSchemeList.append(SlicingList[Waste])

    def PrintAllCuttingScheme(self):
        print("----------------------------------------------------")
        Num = 1
        for CS in self.CuttingSchemeList:
            SlicingList = {}
            for Slicing in CS.Slicing:
                SlicingList[Slicing] = 0

            for Slicing in CS.Slicing:
                SlicingList[Slicing] += 1
            SlicingString = str(SlicingList).replace('{', '').replace('}', '').replace(':', 'x')
            print(f'方案{Num}: 原钢材【{CS.SteelLength}】; 切割【{SlicingString}】; 损耗: {CS.Waste}')
            Num += 1
        print("----------------------------------------------------")


class OrderCuttingScheme:
    CuttingSchemeList: List[CuttingScheme] = None
    AllWaste: int = None
    steelNeedOrder: SteelNeedOrder = None
    SteelLengthList: List[int]

    def __init__(self, steelNeedOrder: SteelNeedOrder):
        self.steelNeedOrder = steelNeedOrder
        self.CuttingSchemeList = []
        self.AllWaste = 0

    def SetSteelLengthList(self, steelLengthList: List[int]):
        self.SteelLengthList = steelLengthList

    def append(self, cuttingScheme: CuttingScheme) -> bool:
        Waste = self.steelNeedOrder.Deduct(cuttingScheme)
        if Waste == -1:
            return False
        else:
            self.CuttingSchemeList.append(cuttingScheme)
            self.AllWaste += cuttingScheme.Waste
            self.AllWaste += Waste
            return True

    def AllSteelNeedAndWasteLength(self) -> int:
        Length = self.AllWaste
        for steelNeed in self.steelNeedOrder.SteelNeedList:
            Length += steelNeed.Length * steelNeed.Quantity
        return Length

    def Print(self, cuttingSchemeList, order: SteelNeedOrder):
        Compose = {}
        for Num in range(0, len(cuttingSchemeList)):
            Compose[Num] = 0

        for Item in self.CuttingSchemeList:
            for Num in range(0, len(cuttingSchemeList)):
                if cuttingSchemeList[Num].Slicing == Item.Slicing and cuttingSchemeList[Num].SteelLength == Item.SteelLength:
                    Compose[Num] += 1

        x = 0
        SlicingStringList = {}
        for CS in cuttingSchemeList:
            SlicingList = {}
            for Slicing in CS.Slicing:
                SlicingList[Slicing] = 0

            for Slicing in CS.Slicing:
                SlicingList[Slicing] += 1
            SlicingString = str(SlicingList).replace('{', '').replace('}', '').replace(':', 'x')
            SlicingStringList[x] = f'原钢材[{CS.SteelLength}]; 切割[{SlicingString}]; 损耗: {CS.Waste}'
            x += 1

        print("----------------------------------------------------")
        order.Print()
        for Num in Compose:
            if Compose[Num] != 0:
                print(f'【{SlicingStringList[Num]}】 X {Compose[Num]}')
        print(f'总损耗：{self.AllWaste}')
        print(f'优化率：{1 - (self.AllWaste / (self.AllWaste + order.GetAllLength()))}')
        print("----------------------------------------------------")


def BottomUp(cuttingSchemeList: List[CuttingScheme],
             orderCuttingScheme: OrderCuttingScheme,
             minWaste: int) -> OrderCuttingScheme:

    f = {0: copy.deepcopy(orderCuttingScheme)}

    for Num in range(1, orderCuttingScheme.steelNeedOrder.GetAllSteelQuantity() + 2):
        f[Num] = copy.deepcopy(f[Num-1])
        NowOrderCuttingScheme = copy.deepcopy(f[Num-1])

        if NowOrderCuttingScheme.steelNeedOrder.isFinish():
            return NowOrderCuttingScheme

        for SelectCuttingScheme in copy.deepcopy(cuttingSchemeList):
            NewOrderCuttingScheme = copy.deepcopy(NowOrderCuttingScheme)

            if NewOrderCuttingScheme.append(SelectCuttingScheme):
                if NewOrderCuttingScheme.AllSteelNeedAndWasteLength() < f[Num].AllSteelNeedAndWasteLength():
                    f[Num] = copy.deepcopy(NewOrderCuttingScheme)
                    continue

                elif NowOrderCuttingScheme.steelNeedOrder.GetAllSteelQuantity() == f[Num].steelNeedOrder.GetAllSteelQuantity():
                    f[Num] = copy.deepcopy(NewOrderCuttingScheme)

        if minWaste < f[Num].AllWaste:
            return f[Num]

        TheOrderCuttingScheme = copy.deepcopy(f[Num])

        Do = True
        while Do:

            NowCuttingScheme = f[Num].CuttingSchemeList[-1]
            Do = TheOrderCuttingScheme.append(NowCuttingScheme)

            if f[Num].AllWaste + NowCuttingScheme.Waste != TheOrderCuttingScheme.AllWaste:
                Do = False

            if Do:
                f[Num] = copy.deepcopy(TheOrderCuttingScheme)
    return f[orderCuttingScheme.steelNeedOrder.GetAllSteelQuantity()]

def GetAllOriginSteelLengthCombination(AllOriginSteelLengthList: list, MaxDifferentLength: int) -> List[list]:
    def append(CombinationList: List[list]) -> List[list]:
        NewCombinationList = []
        if len(CombinationList) == 0:
            for SteelLength in AllOriginSteelLengthList:
                TheCombination = [SteelLength]
                NewCombinationList.append(TheCombination)
        else:
            for NowSteelLength in CombinationList:
                for SteelLength in AllOriginSteelLengthList:
                    TheCombination = copy.deepcopy(NowSteelLength)
                    TheCombination.append(SteelLength)
                    TheCombination.sort()

                    if TheCombination in NewCombinationList:
                        continue

                    NewCombinationList.append(TheCombination)

        return NewCombinationList

    AllOriginSteelLengthCombination: List[list] = []

    for Num in range(0, MaxDifferentLength):
        AllOriginSteelLengthCombination = append(copy.deepcopy(AllOriginSteelLengthCombination))

    return AllOriginSteelLengthCombination


def RunBottomUpTask(Order, AllCuttingScheme, originSteelLengthCombination, result_dict, result_lock):
    CuttingSchemeList = []
    for key in originSteelLengthCombination:
        CuttingSchemeList += AllCuttingScheme[key].GetCuttingSchemeList()

    OCS = OrderCuttingScheme(Order)
    r = BottomUp(CuttingSchemeList, OCS, result_dict['minWaste'])

    with result_lock:
        if result_dict['minWaste'] > r.AllWaste:
            result_dict['minWaste'] = r.AllWaste
            result_dict['BestCuttingSchemeList'] = CuttingSchemeList
            result_dict['BestOrderCuttingScheme'] = r

        result_dict['current'] += 1
        print('\r' + str(result_dict['current']) + '/' + str(result_dict['AllTask']), file=sys.stderr, end='')
    return


def RunCuttingSchemeManageTask(Order, SteelLength, result_dict, result_lock):
    CS = CuttingSchemeManage(Order, [SteelLength])
    with result_lock:
        result_dict[SteelLength] = CS

    return

if __name__ == '__main__':
    startTime = int(time())

    maxLength = 6500
    minLength = 3500
    minUnit = 10
    maxDifferentLength = 3
    num_cores = int(mp.cpu_count())
    print("本地计算机有: " + str(num_cores) + " 核心")

    Order = SteelNeedOrder()

    # Order.append(SteelNeed(1600, 258))
    # Order.append(SteelNeed(840, 10))
    # Order.append(SteelNeed(780, 59))
    # Order.append(SteelNeed(1900, 450))
    # Order.append(SteelNeed(4890, 150))
    # Order.append(SteelNeed(5800, 1540))
    # Order.append(SteelNeed(6100, 800))
    # Order.append(SteelNeed(1500, 160))
    # Order.append(SteelNeed(980, 150))
    # Order.append(SteelNeed(2410, 65))
    # Order.append(SteelNeed(4600, 260))
    # Order.append(SteelNeed(2980, 150))
    # Order.append(SteelNeed(1570, 316))
    # Order.append(SteelNeed(3480, 200))


    # 测试一
    # Order.append(SteelNeed(3000, 152))
    # Order.append(SteelNeed(3100, 256))
    # Order.append(SteelNeed(980, 98))
    # Order.append(SteelNeed(1600, 258))

    # 第一组
    Order.append(SteelNeed(2700, 48))
    Order.append(SteelNeed(3540, 150))
    Order.append(SteelNeed(3150, 80))
    Order.append(SteelNeed(1850, 21))
    Order.append(SteelNeed(970, 60))

    # 第二组
    # Order.append(SteelNeed(615, 77))
    # Order.append(SteelNeed(4800, 136))
    # Order.append(SteelNeed(5120, 110))
    # Order.append(SteelNeed(1170, 60))

    # 第三组
    # Order.append(SteelNeed(2700, 48))
    # Order.append(SteelNeed(3540, 150))
    # Order.append(SteelNeed(3150, 80))
    # Order.append(SteelNeed(1850, 21))
    # Order.append(SteelNeed(970, 60))

    # allOriginSteelLengthList = GetAllOriginSteelLength(Order, maxLength, minLength, minUnit)
    # print(allOriginSteelLengthList)
    # print(len(allOriginSteelLengthList))

    print(f"原条料可用种数{maxDifferentLength}。")
    print(f"原条料浮动间隔{minUnit}。")
    print(f"订单中有{len(Order.SteelNeedList)}条不同长度需求。")
    print(f"订单中总共需要{Order.GetAllSteelQuantity()}条。")

    allOriginSteelLength = list(range(minLength, maxLength + 1, minUnit))

    pool = mp.Pool(num_cores)
    manager = mp.Manager()
    managed_locker = manager.Lock()
    allCuttingScheme = manager.dict()

    results = [
        pool.apply_async(RunCuttingSchemeManageTask,
                         args=(Order, SteelLength, allCuttingScheme, managed_locker))
        for SteelLength in allOriginSteelLength
    ]
    results = [p.get() for p in results]

    BestOriginSteelLengthList = []

    for key in allCuttingScheme:
        print(allCuttingScheme[key].PrintAllCuttingScheme())
        exit()
        if allCuttingScheme[key].HaveComplete:
            BestOriginSteelLengthList.append(key)

    print(f'有{len(BestOriginSteelLengthList)}钢条符合。')

    allOriginSteelLengthCombination = list(combinations(BestOriginSteelLengthList, maxDifferentLength))
    print(f'有{len(allOriginSteelLengthCombination)}组合结果。')
    print("----------------------------------------------------")

    print("开始")
    # BestCuttingSchemeMangeList = [CuttingSchemeManage(Order, [6200, 5940])]
    # BestCuttingSchemeMangeList = [CuttingSchemeManage(Order, [3560, 3560])]
    pool = mp.Pool(num_cores)
    manager = mp.Manager()
    managed_locker = manager.Lock()
    managed_dict = manager.dict()

    managed_dict['minWaste'] = float('inf')
    managed_dict['BestOrderCuttingScheme'] = None
    managed_dict['BestCuttingSchemeList'] = None
    managed_dict['current'] = 0
    managed_dict['AllTask'] = len(allOriginSteelLengthCombination)

    StepCount = 100
    for count in range(0, int(len(allOriginSteelLengthCombination)/StepCount)):
        results = [
            pool.apply_async(RunBottomUpTask, args=(Order, allCuttingScheme, OriginSteelLengthCombination, managed_dict, managed_locker))
            for OriginSteelLengthCombination in allOriginSteelLengthCombination[count*StepCount: (count-1)*StepCount]
        ]
        results = [p.get() for p in results]
        break
    print("")
    print("最后")
    managed_dict['BestOrderCuttingScheme'].Print(managed_dict['BestCuttingSchemeList'], Order)
    endTime = int(time())
    print(f'执行时间 {endTime - startTime} s')
