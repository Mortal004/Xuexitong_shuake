import abc

# 抽象配置器类
class AbstractSetter(abc.ABC):
    __productClassname: str

    def __init__(self, name: str, pClassname: str) -> None:
        self._name = name
        self.__setProductClassname(pClassname)

    # 设置配置类的类型
    @classmethod
    def __setProductClassname(cls, pClassname: str):
        cls.__productClassname = pClassname

    # 获取配置类的类型
    @classmethod
    def getProductClassname(cls):
        return cls.__productClassname


class TableSetter(AbstractSetter):
    def __init__(self, name="") -> None:
        super().__init__(name, "TablePrinter")  # 传入配置类的类型
        """
        序号相关参数
            :autoOrdNumber: 是否开启自动序号
                            True表示开启，False表示关闭
            :ordNumberName: 序号字段的名字
            :ordNumberStart: 序号的开始值
            :ordNumberStep: 序号值间的步长
        """
        self.hasHead = False         # 数据中是否有表头
        self.autoOrdNumber = False  # 是否开启自动序号
        self.ordNumberName = "序号"  # 序号字段的名字
        self.ordNumberStart = 1     # 序号的开始值
        self.ordNumberStep = 1      # 序号的步长
        """
        表格形状相关参数
            :_autoColumnWidth: 自动计算表格中的列宽
                    默认开启自动计算
                    当调用 setTableColWidth() 设置手动设置表格列宽时该功能会关闭

            :alignment: 数据的对齐方式
                    “l” 或 “L” 表示左对齐
                    “r” 或 “R” 表示右对齐
                    “c” 或 “C” 标识居中

            :_tableColumnWidth: 表格中列元素的宽度
                该参数的值通过两种方式设置
                    方式1、程序通过传入的数据自动计算出每列所需的最大宽度，并赋给该参数
                    方式2、通过外部通过调用 setTableColwidth() 方法传入自定义的宽度
                        当通过 setTableColwidth() 程序会将 _autoColumnWidth 的值设置为 False
                    注意：通过方式2设置该参数值是，每列的宽度值大于等于3！

            :margin_left: 数据与单元格左边的距离
            :margin_right: 数据与单元格右边的距离

        """
        self.autoColumnWidth = True    # 是否自动计算表格列宽
        self.alignment = "l"            # 表格中的对齐方式
        self.margin_left = 1            # 左边距
        self.margin_right = 1           # 右边距
        """
        表格外观设置
            :borderChar: 绘制表格边框所用的符号
            :splitChar: 分割单元格所用的符号
            :turnChar: 绘制转折点所用的符号（单元格的顶点）
        """
        self.borderChar = "-"           # 边框符号
        self.splitChar = "|"            # 分割符号
        self.turnChar = "+"             # 转折点符号
        self.abreastTableNumber = 1     # 并排显示的表格数目
        self.tableSplitWidth = 5        # 并排显示的表格间距离
        self.headColor = "white"        # 表头颜色
        self.bodyColor = "white"        # 表主体颜色

    # 获取表格所有列宽数据
    def getTableColWidth(self):
        return self._tableColumnWidth

    # 是否自动计算表格列宽
    def isAutoColumnWidth(self):
        return self.autoColumnWidth


# 消息控制器
class MsgSetter(AbstractSetter):
    def __init__(self, name: str = ""):
        super().__init__(name, "MsgPrinter")
        self.horizontalSymbol = "="     # 上下边框的符号
        self.verticalSymbol = "|"       # 两侧边框的符号
        self.color = "white"            # 显示的颜色
        self.margin_left = 1            # 左边距
        self.margin_right = 1           # 右边距


# 分隔线控制器
class SplitSetter(AbstractSetter):
    def __init__(self, name: str = ""):
        super().__init__(name, "SplitPrinter")
        self.symbol = "-"
        self.length: int = 50
        self.color = "white"
        self.frontNewlineNumber: int = 1
        self.behindNewlineNumber: int = 1
        self.message: str = ""
        self.leftmostSymbol = self.symbol
        self.rightmostSymbol = self.symbol

