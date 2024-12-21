from task.tool.printer import *
from task.tool.setter import AbstractSetter

nameSpace = locals()


def getPrinterBySetter(setter: AbstractSetter) -> AbstractPrinter:
    try:
        obj_class = nameSpace[setter.getProductClassname()]
        obj = obj_class()
        obj.setSetter(setter)
    except KeyError:
        raise KeyError("Printer.py 中没有与传入 Setter 实例匹配的类")
    return obj


def getPrinterByName(printerName: str) -> AbstractPrinter:
    try:
        obj_class = nameSpace[printerName]
    except KeyError:
        raise KeyError("printer.py模块中没有 {} 类".format(printerName))
    return obj_class()

