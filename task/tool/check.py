import cv2
import numpy
import pyautogui


def check(name,threshold = 0.8):
    try:
        pyautogui.locateOnScreen(r'task\img\img_'+f'{name}'+'.png', confidence=threshold)
        return True
    except:
        return False

def find_image_on_screen(name,reg=(0,0,1920,1080),threshold = 0.8):
    # 读取模板图像
    template = cv2.imread(r'task\img\img_'+f'{name}'+'.png', 0) # 以灰度模式读取图像

    # 获取屏幕截图并转换为灰度图像
    screen = pyautogui.screenshot(region=reg)
    screen_rgb = numpy.array(screen)
    gray_screen = cv2.cvtColor(screen_rgb, cv2.COLOR_BGR2GRAY)

    # 模板匹配
    result = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)

    # 获取匹配位置
    loc = numpy.where(result >= threshold)
    points = list(zip(*loc[::-1])) # 将匹配位置转换为Python列表

    if points:
        # 获取匹配区域的中心点
        x, y = points[0]
        w, h = template.shape[::-1]
        center_x = x + w // 2
        center_y = y + h // 2
        return center_x,center_y,y-10
    else:
        return False
