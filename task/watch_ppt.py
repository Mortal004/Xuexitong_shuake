import time

from selenium.webdriver.common.by import By

from task.tool import color


def __ppt(driver):
    print(color.green("正在检索PPT数量..."))
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
    element = driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
    driver.switch_to.frame(element)
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="panView"]'))

    imgList = driver.find_elements(By.TAG_NAME, 'li')
    print(color.green("共有{}张PPT".format(len(imgList))))
    for i in range(len(imgList)):
        # print('\r'+"观看第{}张PPT".format(i+1), end="")
        driver.execute_script("window.scrollBy(0,2000)")
        # time.sleep(0.1)

    print('已看完ppt,点击下一节')

    return
