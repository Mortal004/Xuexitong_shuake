
import abc

# 第三方库
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

class Task(abc.ABC):
    def __init__(self, driver: WebDriver):
        self.__driver = driver

    @abc.abstractmethod
    def isCurrentTask(self, iframeIndex) -> bool:
        pass

    @abc.abstractmethod
    def finish(self):
        pass


class Answerable(abc.ABC):
    @abc.abstractmethod
    def getAnswerWebElement(self) -> list[WebElement]:
        pass
