import copy
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

    def __init__(self, SteelLength: int, Slicing: list):
        self.SteelLength = SteelLength
        self.Waste = SteelLength
        self.Slicing = Slicing.copy()

        for Num in Slicing:
            self.Waste = self.Waste - Num


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

    def __init__(self, order: SteelNeedOrder, SteelLengthList: List[int]):
        self.Order = order
        self.SteelLengthList = SteelLengthList
        self.ComposeList = []
        self.CuttingSchemeList = []

        for SteelLength in list(set(SteelLengthList)):
            self.ComposeList.clear()
            self.__AddSlicing(SteelLength, SteelLength, [], self.Order.GetAllSteelNeedLengthList())

    def __AddSlicing(self, OriginalSteelLength: int, NowSteelLength: int, NowSlicing: list, NeedList: list):
        def append():
            TheNowSlicing.append(NeedLength)
            TheNowSlicing.sort()
            if TheNowSlicing not in self.ComposeList:
                self.ComposeList.append(TheNowSlicing)
                self.CuttingSchemeList.append(CuttingScheme(OriginalSteelLength, TheNowSlicing))

        for NeedLength in NeedList:
            TheNowSlicing = NowSlicing.copy()
            if NowSteelLength > NeedLength:
                append()
                self.__AddSlicing(OriginalSteelLength, NowSteelLength - NeedLength, TheNowSlicing.copy(), NeedList)
            elif NeedLength == NowSteelLength:
                append()

    def GetCuttingSchemeList(self) -> List[CuttingScheme]:
        return self.CuttingSchemeList

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
             orderCuttingScheme: OrderCuttingScheme) -> OrderCuttingScheme:

    f = {0: copy.deepcopy(orderCuttingScheme)}

    for Num in range(1, orderCuttingScheme.steelNeedOrder.GetAllSteelQuantity() + 2):
        f[Num] = copy.deepcopy(f[Num-1])
        NowOrderCuttingScheme = copy.deepcopy(f[Num-1])

        for SelectCuttingScheme in copy.deepcopy(cuttingSchemeList):
            NewOrderCuttingScheme = copy.deepcopy(NowOrderCuttingScheme)
            if NewOrderCuttingScheme.steelNeedOrder.isFinish():
                return NewOrderCuttingScheme

            if NewOrderCuttingScheme.append(SelectCuttingScheme):
                if NewOrderCuttingScheme.AllSteelNeedAndWasteLength() < f[Num].AllSteelNeedAndWasteLength():
                    f[Num] = copy.deepcopy(NewOrderCuttingScheme)
                    continue

                elif NowOrderCuttingScheme.steelNeedOrder.GetAllSteelQuantity() == f[Num].steelNeedOrder.GetAllSteelQuantity():
                    f[Num] = copy.deepcopy(NewOrderCuttingScheme)

        TheOrderCuttingScheme = copy.deepcopy(f[Num])

        Do = True
        while Do:

            NowCuttingScheme = f[Num].CuttingSchemeList[-1]
            Do = TheOrderCuttingScheme.append(NowCuttingScheme)

            if f[Num].AllWaste + NowCuttingScheme.Waste != TheOrderCuttingScheme.AllWaste:
                Do = False

            if Do:
                f[Num] = copy.deepcopy(TheOrderCuttingScheme)

        f[Num].Print(copy.deepcopy(cuttingSchemeList), orderCuttingScheme.steelNeedOrder)
    return f[orderCuttingScheme.steelNeedOrder.GetAllSteelQuantity()]


def GetAllOriginSteelLength(order: SteelNeedOrder, MaxLength: int, MinLength, MinUnit: int) -> list:

    MaxLengthList = {}
    AllSteelLengthScheme: List[list] = []
    AllOriginSteelLength = []

    for NeedSteel in order.SteelNeedList:
        MaxLengthList[NeedSteel.Length] = (int(MaxLength / NeedSteel.Length))

    MaxLengthList = sorted(MaxLengthList.items(), key=lambda d: d[0])

    print(MaxLengthList)
    exit()
    x = 0
    for Key, Value in MaxLengthList:
        NowSteelLength: List[list] = []

        if x == 0:
            BeforeSteelLengthScheme = []
        else:
            BeforeSteelLengthScheme = AllSteelLengthScheme[x - 1]

        for Num in range(0, Value + 1):
            if len(BeforeSteelLengthScheme) == 0:
                New = BeforeSteelLengthScheme[:]
                New.append(Num)
                NowSteelLength.append(New)
            else:
                for New in BeforeSteelLengthScheme:
                    TheNew = New[:]
                    TheNew.append(Num)
                    NowSteelLength.append(TheNew)

        for TheSteelScheme in NowSteelLength:
            NewOriginSteelLength = 0
            for Num in range(0, len(TheSteelScheme)):
                NewOriginSteelLength += Key * TheSteelScheme[Num]

            NewOriginSteelLength += NewOriginSteelLength % MinUnit

            if MinLength <= NewOriginSteelLength <= MaxLength and NewOriginSteelLength not in AllOriginSteelLength:
                AllOriginSteelLength.append(NewOriginSteelLength)
        AllSteelLengthScheme.append(NowSteelLength)
        x += 1

    AllOriginSteelLength.sort()

    return AllOriginSteelLength


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


if __name__ == '__main__':
    startTime = int(time())

    maxLength = 6500
    minLength = 3500
    minUnit = 10
    maxDifferentLength = 3

    Order = SteelNeedOrder()

    Order.append(SteelNeed(1600, 258))
    Order.append(SteelNeed(840, 10))
    Order.append(SteelNeed(780, 59))
    Order.append(SteelNeed(1900, 450))
    Order.append(SteelNeed(4890, 150))
    Order.append(SteelNeed(5800, 1540))
    Order.append(SteelNeed(6100, 800))
    Order.append(SteelNeed(1500, 160))
    Order.append(SteelNeed(980, 150))
    Order.append(SteelNeed(2410, 65))
    Order.append(SteelNeed(4600, 260))
    Order.append(SteelNeed(2980, 150))
    Order.append(SteelNeed(1570, 316))
    Order.append(SteelNeed(3480, 200))


    # 测试一
    # Order.append(SteelNeed(3000, 152))
    # Order.append(SteelNeed(3100, 256))
    # Order.append(SteelNeed(980, 98))
    # Order.append(SteelNeed(1600, 258))

    # 第一组
    # Order.append(SteelNeed(2700, 48))
    # Order.append(SteelNeed(3540, 150))
    # Order.append(SteelNeed(3150, 80))
    # Order.append(SteelNeed(1850, 21))
    # Order.append(SteelNeed(970, 60))

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

    allOriginSteelLengthList = GetAllOriginSteelLength(Order, maxLength, minLength, minUnit)
    print(allOriginSteelLengthList)
    print(len(allOriginSteelLengthList))

    CSMange = CuttingSchemeManage(Order, allOriginSteelLengthList)

    CSMange.PrintAllCuttingScheme()

    BottomUp(CSMange.GetCuttingSchemeList(), OrderCuttingScheme(Order))
    exit()
    allOriginSteelLengthCombination = GetAllOriginSteelLengthCombination(allOriginSteelLengthList, maxDifferentLength)

    # print(allOriginSteelLengthCombination)
    AllTask = Order.GetAllSteelQuantity() * len(allOriginSteelLengthCombination)
    PB = ProgressBar(AllTask, fmt=ProgressBar.FULL)

    AllOrderCuttingScheme = {}

    BestCuttingSchemeMangeList: list[CuttingSchemeManage] = []
    BestCuttingSchemeMaxClearNum = -1

    for OriginSteelLengthCombination in allOriginSteelLengthCombination:
        CSMange = CuttingSchemeManage(Order, OriginSteelLengthCombination)

        CuttingSchemeList = CSMange.GetCuttingSchemeList()

        MaxClearNum = 0
        for s in CuttingSchemeList:
            if s.Waste == 0:
                MaxClearNum += 1

        if MaxClearNum > BestCuttingSchemeMaxClearNum:
            BestCuttingSchemeMangeList = [copy.deepcopy(CSMange)]
            BestCuttingSchemeMaxClearNum = MaxClearNum

        elif MaxClearNum == BestCuttingSchemeMaxClearNum:
            BestCuttingSchemeMangeList.append(copy.deepcopy(CSMange))

    PB = ProgressBar(len(BestCuttingSchemeMangeList), fmt=ProgressBar.FULL)

    AllOrderCuttingScheme = {}

    # BestCuttingSchemeMangeList = [CuttingSchemeManage(Order, [6200, 5940])]
    # BestCuttingSchemeMangeList = [CuttingSchemeManage(Order, [3560, 3560])]
    minWaste = float('inf')
    minWasteNum = 0
    minSteelLengthList = []
    for OriginSteelLengthCombination in BestCuttingSchemeMangeList:
        # TheMinWaste = float('inf')
        # TheMinWasteNum = 0
        # for s in OriginSteelLengthCombination.CuttingSchemeList:
        #     if s.Waste != 0 and s.Waste < TheMinWaste:
        #         TheMinWaste = s.Waste
        #         TheMinWasteNum = 1
        #     elif s.Waste == TheMinWaste:
        #         TheMinWasteNum += 1
        #
        # if TheMinWaste < minWaste:
        #     minSteelLengthList = OriginSteelLengthCombination.SteelLengthList
        #     minWaste = TheMinWaste
        # elif TheMinWaste == minWaste and minWasteNum > TheMinWasteNum:
        #     minSteelLengthList = OriginSteelLengthCombination.SteelLengthList
        #     minWaste = TheMinWaste
        # OriginSteelLengthCombination.PrintAllCuttingScheme()
        # print(f'{OriginSteelLengthCombination.SteelLengthList}: 总损耗, 总')
        # continue

        CuttingSchemeList = OriginSteelLengthCombination.GetCuttingSchemeList()
        # OriginSteelLengthCombination.PrintAllCuttingScheme()
        # print(OriginSteelLengthCombination.SteelLengthList)

        OCS = OrderCuttingScheme(Order)
        OCS.SetSteelLengthList(OriginSteelLengthCombination.SteelLengthList)

        r = BottomUp(CuttingSchemeList, OCS)
        # r.Print(CuttingSchemeList, Order)
        PB()
        PB.current += 1

        AllOrderCuttingScheme[r.AllWaste] = [r, CuttingSchemeList]

    minWaste = float('inf')
    for Waste in AllOrderCuttingScheme:
        if minWaste > Waste:
            minWaste = Waste

    print("最后")
    # print(minSteelLengthList)

    # exit()
    minOrderCuttingScheme = AllOrderCuttingScheme[minWaste]
    minOrderCuttingScheme[0].Print(minOrderCuttingScheme[1], Order)

    endTime = int(time())
    print(f'执行时间 {endTime - startTime} s')
