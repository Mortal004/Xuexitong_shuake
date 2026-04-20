from task.tool import color
from selenium.webdriver.common.by import By
import time
import pickle
import json
import traceback
from task.tool.send_wx import send_error

def check_face(driver,face_url,face_class='popDiv wid640 faceCollectQrPop popClass',course_name=''):
    i = 0
    while i <= 200:
        try:
            driver.find_element(By.CSS_SELECTOR, f"[class='{face_class}']")
            if i == 0:
                print(color.red('已检测人脸认证弹窗'),flush=True)
                if auto_login_with_cookies(driver,file_name='face_cookies',url=face_url,face_class=face_class):
                    return
            if i == 0 :
                print(color.red('请按照要求手机扫码进行人脸认证,如有误判将在20秒后默认您已经完成认证'), flush=True)
            time.sleep(1)
            i += 1
        except:
            if i != 0:
                print(color.red('人脸认证已完成'), flush=True)
                get_cookie(driver,file_name='face_cookies',course_name=course_name)
            break
def get_cookie(driver,file_name='cookies',course_name=''):
    try:
        pickle.dump(driver.get_cookies(), open(rf'task/tool/{file_name}.pkl', 'wb'))
        if file_name=='face_cookies':
            with open(rf'task/tool/account_info.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                data[course_name] = driver.current_url
                # print(data['face_url'], flush=True)
                json.dump(data, open(rf'task/tool/account_info.json', 'w', encoding='utf-8'))
        return True
    except PermissionError:
        print(color.red('请在关闭该窗口后，再右键点击刷课程序用管理员权限打开'))
        return False
    except Exception :
        print(color.red(f'获取cookie失败'),flush=True)
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n" + error_msg)
        return True


def auto_login_with_cookies(driver,file_name='cookies', url='https://i.chaoxing.com',face_class='popDiv wid640 faceCollectQrPop popClass'):
    if not driver.title=='用户登录' and file_name=='cookies':
        return True
    try:
        # 清除可能存在的旧cookie
        # driver.delete_all_cookies()
        try:
            cookies = pickle.load(open(rf'task/tool/{file_name}.pkl', 'rb'))
        except:
            return False
        print(color.green('正在尝试自动跳过。。。'),flush=True)
        # 逐个添加cookie
        for cookie in cookies:
            try:
                # 移除可能引起问题的属性
                cookie_to_add = cookie.copy()
                # Selenium的add_cookie方法不支持'sameSite'参数，需要移除
                if 'sameSite' in cookie_to_add:
                    del cookie_to_add['sameSite']
                # 确保domain格式正确
                if cookie_to_add['domain'].startswith('.'):
                    # 对于以点开头的domain，确保浏览器在当前域的正确上下文中
                    pass
                driver.add_cookie(cookie_to_add)
                # print(color.green(f"成功添加cookie: {cookie['name']}"),flush=True)
            except Exception as e:
                pass
                # print(color.red(f"添加cookie {cookie['name']} 时出错: {e}"),flush=True)

        # 刷新页面使cookie生效
        driver.refresh()

        # 等待页面加载
        time.sleep(3)
        #  访问需要登录的页面测试
        test_url = url  # 个人中心页面
        if test_url:
            driver.get(test_url)
        # 验证登录是否成功
        if file_name=='face_cookies':
            try:
                driver.find_element(By.CSS_SELECTOR, f"[class='{face_class}']")
                print(color.red('跳过人脸认证失败'), flush=True)
                return False
            except:
                print(color.green('成功跳过人脸认证'),flush=True)
                return True

        if driver.title!='用户登录' :
            print(color.green("自动登录验证成功！"),flush=True)
            return True
        else:
            print(color.red("登录可能已过期"),flush=True)
            return False

    except Exception as e:
        print(color.red(f"自动登录过程中出错"),flush=True)
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n" + error_msg)
        return False
