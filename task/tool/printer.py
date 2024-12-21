from math import ceil
from task.tool import color
from task.tool.setter import *

# 抽象打印器类
class AbstractPrinter(abc.ABC):
    def __init__(self):
        self._setter: AbstractSetter = None      # 保存打印器的配置器

    # 设置打印器的配置器
    @abc.abstractmethod
    def setSetter(self, setter: AbstractSetter):
        pass

    # 判断打印器的设置器是否为空
    # 如果设置器不为空则什么都不做，如果为空则创建一个默认的设置器
    # 具体打印器需要什么设置器又子类实现
    @abc.abstractmethod
    def _isSetterNone(self):
        pass

    # 将传入的数据进行预处理
    @abc.abstractmethod
    def _preprocessing(self, data):
        pass

    # 将数据输出
    @abc.abstractmethod
    def _printOut(self, data):
        pass

    # 重置属性
    @abc.abstractmethod
    def _resetProperties(self):
        pass

    # 每个打印器的入口
    # 该方法规定了打印器中方法调用的顺序
    def print(self, data=None):
        self._isSetterNone()
        data = self._preprocessing(data)
        self._printOut(data)
        self._resetProperties()

    # 获取字符的显示宽度
    @staticmethod
    def _getCharWidth(char):
        o = ord(char)
        widths = [
            (126,    1), (159,    0), (687,     1), (710,   0), (711,   1),
            (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0),
            (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1),
            (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2),
            (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
            (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
            (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
            (120831, 1), (262141, 2), (1114109, 1),
        ]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    # 获取字符串的显示宽度
    def _getStringWidth(self, string):
        width = 0
        for char in string:
            width += self._getCharWidth(char)
        return width


# 表格打印器
class TablePrinter(AbstractPrinter):
    # 默认单元格宽度
    _defaultGridWidth = 5

    def __init__(self) -> None:
        super().__init__()
        self._tableColumnWidth = []     # 表格中每列的宽度
        self._dataWidths: list[list]
        self._line: str
        self._xMax: int
        self._yMax: int
        self._head: list
        self._headWidths: list

    def setSetter(self, setter: TableSetter):
        self._setter = setter

    def _isSetterNone(self):
        if self._setter is not None:
            return
        self._setter = TableSetter()

    def _preprocessing(self, dataList):
        """
        将数据标准化
        """
        # 获取数据中的最大行的元素个数
        standardKey = 0  # 用于标记数据是否是标准的，大于一表示不标准
        maxRowLength = 0  # 保存数据中元素最多的行的元素个数
        for row in dataList:
            rowLength = len(row)
            if rowLength > maxRowLength:
                maxRowLength = rowLength
            if rowLength != maxRowLength:
                standardKey += 1

        if standardKey > 1:
            # 补全数据
            for index in range(len(dataList)):
                differ = maxRowLength - len(dataList[index])
                dataList[index] += ["" for _ in range(differ)]

        """
        向数据中添加序号，这一步之后表格的长宽就不会变了
        """
        if self._setter.autoOrdNumber:
            starNumber = self._setter.ordNumberStart
            step = self._setter.ordNumberStep
            title = self._setter.ordNumberName
            hasHead = self._setter.hasHead

            # 添加字段名
            start: int  # 开始添加位置
            if hasHead:
                start = 1
                dataList[0].insert(0, title)
            else:
                start = 0
            for i in range(start, len(dataList)):
                dataList[i].insert(0, starNumber)
                starNumber += step
            if not self._setter.isAutoColumnWidth():
                shapeList = self._tableColumnWidth
                numberWidth = self._getStringWidth(str(starNumber))
                if numberWidth <= 5:
                    shapeList.insert(0, 5)
                else:
                    shapeList.insert(0, numberWidth)
                self._tableColumnWidth = shapeList
        self._xMax = len(dataList[0])
        self._yMax = len(dataList)

        """
        讲超过将超过用户指定长度的数据改为省略显示
        """
        widths = [[0 for _ in range(self._xMax)] for _ in range(self._yMax)]
        tableWidths = [0 for _ in range(self._xMax)]
        # 按列进行扫描
        for x in range(self._xMax):
            for y in range(self._yMax):
                dataList[y][x] = str(dataList[y][x])  # 将所有数据都转为字符串形
                if self._setter.isAutoColumnWidth():
                    # 自动生成表格形状
                    widths[y][x] = self._getStringWidth(dataList[y][x])
                    if widths[y][x] > tableWidths[x]:
                        tableWidths[x] = widths[y][x]
                else:
                    # 进行省略显示操作
                    if self._getStringWidth(dataList[y][x]) > self._tableColumnWidth[x]:
                        strItem = dataList[y][x]
                        while self._getStringWidth(strItem) + 3 > self._tableColumnWidth[x]:
                            strItem = strItem[:len(strItem) // 2]
                        dataList[y][x] = strItem + "..."
                    widths[y][x] = self._getStringWidth(dataList[y][x])
        self._dataWidths = widths
        if self._setter.isAutoColumnWidth():
            self._tableColumnWidth = tableWidths

        """
        如果有表头就将表头提取出来
        """
        if self._setter.hasHead:
            self._head = dataList[0]
            self._headWidths = self._dataWidths[0]
            dataList = dataList[1:]
            self._dataWidths = self._dataWidths[1:]
            self._yMax -= 1

        self._createLine()
        return dataList

    # 打印表格
    def _printOut(self, dataList):
        # 获取配置信息
        splitChar = self._setter.splitChar
        tableShap = self._tableColumnWidth
        margin_left = self._setter.margin_left
        margin_right = self._setter.margin_right
        abreastTableNumber = self._setter.abreastTableNumber
        tableSplitChar = " " * self._setter.tableSplitWidth
        hasHead = self._setter.hasHead

        step = ceil(self._yMax / abreastTableNumber)  # 计算不步长
        tables = []
        # 需要显示的表格数将数据切片保存到 tables 中
        for i in range(step):
            item = dataList[i::step]
            # 判断数据是否够
            # 如果不够则补充空数据，并且在_dataWidths中添加上对应数据位置的宽度
            if len(item) < abreastTableNumber:
                for n in range(abreastTableNumber - len(item)):
                    item.append(["" for _ in range(self._xMax)])
                    self._dataWidths.append([0 for _ in range(self._xMax)])
            tables.append(item)

        headColor = self._setter.headColor
        bodyColor = self._setter.bodyColor
        try:
            headColorize = getattr(color, headColor)
            bodyColorize = getattr(color, bodyColor)
        except AttributeError:
            raise Exception("传入的颜色参数错误，color.py中没有名为 {} 或 {} 的函数".format(headColor, bodyColor))

        # 打印表头
        if hasHead:
            heads = []
            for t in range(abreastTableNumber):
                head = splitChar
                for cIndex in range(len(self._head)):
                    if self._setter.alignment in "lL":
                        spaceBefore = " " * margin_left
                        spaceAfter = " " * (tableShap[cIndex] - self._headWidths[cIndex] + margin_right)
                    elif self._setter.alignment in "rR":
                        spaceBefore = " " * (tableShap[cIndex] - self._headWidths[cIndex] + margin_left)
                        spaceAfter = " " * margin_right
                    elif self._setter.alignment in "cC":
                        spaceCount = tableShap[cIndex] - self._headWidths[cIndex]
                        start = spaceCount // 2
                        end = spaceCount - start
                        spaceBefore = " " * (start + margin_left)
                        spaceAfter = " " * (end + margin_right)
                    else:
                        raise Exception("配置的表格对齐方式'{}'是错误的".format(self._setter.alignment))
                    head += spaceBefore + self._head[cIndex] + spaceAfter + splitChar
                heads.append(head)
            print(headColorize(self._line))
            print(headColorize(tableSplitChar.join(heads)))

        # 打印表格主体
        for rIndex in range(len(tables)):
            rowList = []
            for tIndex in range(len(tables[rIndex])):
                row = splitChar
                for cIndex in range(len(tables[rIndex][tIndex])):
                    if self._setter.alignment in "lL":
                        spaceBefore = " " * margin_left
                        spaceAfter = " " * (tableShap[cIndex] - self._dataWidths[tIndex * step + rIndex][cIndex] + margin_right)
                    elif self._setter.alignment in "rR":
                        spaceBefore = " " * (tableShap[cIndex] - self._dataWidths[tIndex * step + rIndex][cIndex] + margin_left)
                        spaceAfter = " " * margin_right
                    elif self._setter.alignment in "cC":
                        spaceCount = tableShap[cIndex] - self._dataWidths[tIndex * step + rIndex][cIndex]
                        start = spaceCount // 2
                        end = spaceCount - start
                        spaceBefore = " " * (start + margin_left)
                        spaceAfter = " " * (end + margin_right)
                    else:
                        raise Exception("配置的表格对齐方式'{}'是错误的".format(self._setter.alignment))
                    row += spaceBefore + tables[rIndex][tIndex][cIndex] + spaceAfter + splitChar
                # 加上表格之间的分割符
                rowList.append(row)
            print(bodyColorize(self._line))
            print(bodyColorize(tableSplitChar.join(rowList)))
        print(bodyColorize(self._line))

    def _resetProperties(self):
        self._tableColumnWidth.clear()
        self._dataWidths.clear()
        self._line = None
        self._xMax = None
        self._yMax = None
        self._head = None
        self._headWidths = None

    # 手动设置表格单元格的宽度
    def setTableColWidth(self, tableColWidth):
        # 检测出入参数是否符合标准
        for i in range(len(tableColWidth)):
            if tableColWidth[i] < 3:
                raise Exception("表格列宽中的的元素的值不能小于3，当前{}个元素的值为{}".format(i + 1, tableColWidth[i]))
        self._tableColumnWidth = tableColWidth
        self._setter.autoColumnWidth = False

    # 生成表格的边框线
    def _createLine(self):
        # 获取配置信息
        turnChar = self._setter.turnChar
        borderChar = self._setter.borderChar
        margin_left = self._setter.margin_left
        margin_right = self._setter.margin_right
        tableSplitChar = self._setter.tableSplitWidth * " "
        abreastTableNumber = self._setter.abreastTableNumber

        row = []
        for tIndex in range(abreastTableNumber):
            line = turnChar
            for i in self._tableColumnWidth:
                line += borderChar * (i + margin_left + margin_right) + turnChar
            row.append(line)
        self._line = tableSplitChar.join(row)


# 消息打印器
class MsgPrinter(AbstractPrinter):
    def __init__(self):
        super().__init__()
        self._maxSize = 0
        self._msgWidths = []

    def setSetter(self, setter: MsgSetter):
        self._setter = setter

    def _isSetterNone(self):
        if self._setter is not None:
            return
        self._setter = MsgSetter()

    def _preprocessing(self, msg: str) -> list:
        msgList = msg.split("\n")
        for i in msgList:
            size = super()._getStringWidth(i)
            self._msgWidths.append(size)
            if size > self._maxSize:
                self._maxSize = size
        return msgList

    def _printOut(self, msgList: list):
        horizontalSymbol = self._setter.horizontalSymbol
        verticalSymbol = self._setter.verticalSymbol
        marginLeft = self._setter.margin_left
        marginRight = self._setter.margin_right
        colorType = self._setter.color

        try:
            colorize = getattr(color, colorType)
        except AttributeError:
            raise Exception("传入的颜色参数错误，color.py中没有名为 {} 的函数".format(colorType))

        line = horizontalSymbol * (marginLeft + self._maxSize + marginRight + 2)
        print(colorize(line))
        for index in range(len(msgList)):
            front = verticalSymbol + " " * marginLeft
            behind = " " * (self._maxSize - self._msgWidths[index] + marginRight) + verticalSymbol
            print(colorize(front + msgList[index] + behind))
        print(colorize(line))

    def _resetProperties(self):
        self._maxSize = 0
        self._msgWidths.clear()


class SplitPrinter(AbstractPrinter):
    def __init__(self):
        super().__init__()

    def setSetter(self, setter: SplitSetter):
        self._setter = setter

    def _isSetterNone(self):
        if self._setter is not None:
            return
        self._setter = SplitSetter()

    def _preprocessing(self, data):
        return data

    def _printOut(self, length):
        length = self._setter.length
        symbol = self._setter.symbol
        colorType = self._setter.color
        frontNewlineNumber = self._setter.frontNewlineNumber
        behindNewlineNumber = self._setter.behindNewlineNumber
        message = self._setter.message
        lSymbol = self._setter.leftmostSymbol
        rSymbol = self._setter.rightmostSymbol

        try:
            colorize = getattr(color, colorType)
        except AttributeError:
            raise Exception("传入的颜色参数错误，color.py中没有名为 {} 的函数".format(colorType))
        bNumber = length // 2
        aNumber = length - bNumber
        line = "\n"*frontNewlineNumber + lSymbol + symbol*bNumber + message + symbol*aNumber + rSymbol + "\n"*behindNewlineNumber
        print(colorize(line))

    def _resetProperties(self):
        pass

