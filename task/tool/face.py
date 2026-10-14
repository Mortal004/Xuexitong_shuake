# -*- coding: utf-8 -*-

import hashlib
import random
import time
from io import BytesIO
from urllib.parse import urlparse, parse_qs, unquote, quote
from selenium.webdriver.support import expected_conditions as EC

import numpy as np
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from task.tool import color
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
            with open(rf'task/tool/face_url.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                data[course_name] = driver.current_url
                # print(data['face_url'], flush=True)
                json.dump(data, open(rf'task/tool/face_url.json', 'w', encoding='utf-8'))
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
    if '登录' not in driver.title and file_name=='cookies':
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

class ChaoxingFaceBypass:
    """超星人脸识别自动处理"""

    # ============ 常量 ============
    DES_KEY = "Z(AfY@XS"                      # inf_enc 签名盐
    FACE_ENC_SALT = "uWwjeEKsri"              # enc = MD5(puid + salt)
    FACE_API_TOKEN = "4faa8662c59590c6f43ae9fe5b002b42"

    USER_AGENT = (
        "Mozilla/5.0 (Linux; Android 12; SM-N9006 Build/V417IR; wv) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
        "Chrome/101.0.4951.61 Safari/537.36 "
        "(schild:a6aba57d51661f412e8b8d2177adf8b4) (device:SM-N9006) "
        "Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_6.4.5_android_phone_10831_263 "
        "(@Kalimdor)_6e98c17c08204755905e1537b1933e72"
    )

    MAX_RETRIES = 10      # 最大重试次数
    RETRY_DELAY = 5       # 重试间隔（秒）

    def __init__(self, driver, verbose=True):
        self.driver = driver
        self.verbose = verbose
        self.http = requests.Session()
        self.last_qr_url = None
        self.is_processing = False

    # ---------------------------------------------------------------- 日志
    def log(self, msg, level="INFO"):
        # if self.verbose or level in ("ERROR", "WARN"):
        #     print(f"[超星人脸助手][{level}] {msg}")
        pass
    # ------------------------------------------------------- Cookie 同步
    def _cookie_header(self) -> str:
        """把浏览器 Cookie 拼成 Cookie 请求头"""
        return "; ".join(
            f"{c['name']}={c['value']}" for c in self.driver.get_cookies()
        )

    def _headers(self, extra: dict = None) -> dict:
        h = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Referer": self.driver.current_url,
            "Cookie": self._cookie_header(),
        }
        if extra:
            h.update(extra)
        return h

    def get_uid(self):
        """从浏览器 Cookie 中取出 _uid"""
        for c in self.driver.get_cookies():
            if c["name"] == "_uid":
                return c["value"]
        return None

    # -------------------------------------------------------------- 签名
    @classmethod
    def add_inf_enc_sign(cls, params: dict) -> dict:
        """
        复刻 JS：
            query  = k1=v1&k2=v2...&DESKey=Z(AfY@XS
            inf_enc = MD5(query)
        """
        parts = [
            f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
            for k, v in params.items()
            if v is not None
        ]
        query = "&".join(parts) + f"&DESKey={cls.DES_KEY}"
        signed = dict(params)
        signed["inf_enc"] = hashlib.md5(query.encode("utf-8")).hexdigest()
        return signed

    # ---------------------------------------------------------- 参数提取
    def _extract_qr_url(self):
        """读取 #fcqrimg 的 src"""
        return self.driver.execute_script(
            "var el = document.getElementById('fcqrimg');"
            "return (el && el.src) ? el.src : null;"
        )

    @staticmethod
    def _parse_url_params(url: str) -> dict:
        """解析 URL 参数；若含 content 参数则再解析其嵌套 URL"""
        params = {}
        try:
            parsed = urlparse(url)
            for k, v in parse_qs(parsed.query).items():
                params[k] = v[0]
        except Exception as e:
            print(f"[解析URL失败] {e}",flush=True)
            return params

        content = params.get("content")
        if content:
            try:
                decoded = unquote(content)
                inner = parse_qs(urlparse(decoded).query)
                for k, v in inner.items():
                    params[k] = v[0]
                # 特别处理：content 里的 enc 视作 qrcEnc
                if "enc" in inner:
                    params["qrcEnc"] = inner["enc"][0]
            except Exception as e:
                print(f"[解析content失败] {e}",flush=True)
        return params

    def _extract_hidden_fields(self) -> dict:
        """抓取页面上所有有 id 的 hidden input"""
        return self.driver.execute_script("""
            var fields = {};
            document.querySelectorAll('input[type="hidden"]').forEach(function (el) {
                if (el.id && el.value) { fields[el.id] = el.value; }
            });
            return fields;
        """) or {}

    def get_all_params(self, force=True):
        """
        汇总所有必要参数：
          courseid / clazzid / cpi / knowledgeid / uuid / qrcEnc ...
        优先级：QR 码 URL 参数 > content 内层参数 > 隐藏字段 > 当前页面 URL
        """
        qr_url = self._extract_qr_url()
        if not qr_url:
            self.log("未找到 #fcqrimg 元素，可能人脸弹窗还没出现", "WARN")
            return None

        if not force and qr_url == self.last_qr_url:
            self.log("QR 码 URL 未变化（仍返回参数）")
        self.last_qr_url = qr_url
        self.log(f"QR URL: {qr_url}")

        qr_params = self._parse_url_params(qr_url)
        hidden = self._extract_hidden_fields()

        cur = {}
        try:
            p = urlparse(self.driver.current_url)
            for k, v in parse_qs(p.query).items():
                cur[k] = v[0]
        except Exception:
            pass

        # UUID 来源优先级：QR 参数 > 隐藏字段 > 当前 URL
        uuid = qr_params.get("uuid") or hidden.get("uuid") or cur.get("uuid")
        uuid_src = ("QR" if qr_params.get("uuid")
                    else "hidden" if hidden.get("uuid") else "url")
        self.log(f"UUID 来源: {uuid_src}, 值: {uuid}")

        all_params = {}
        all_params.update(qr_params)
        all_params.update(hidden)
        all_params["courseid"] = (qr_params.get("courseid")
                                  or hidden.get("curCourseId")
                                  or cur.get("courseid"))
        all_params["clazzid"] = (qr_params.get("clazzid")
                                 or hidden.get("curClazzId")
                                 or cur.get("clazzid"))
        all_params["cpi"] = (qr_params.get("cpi")
                             or hidden.get("curCpi")
                             or cur.get("cpi"))
        all_params["knowledgeid"] = (qr_params.get("knowledgeid")
                                     or hidden.get("curChapterId")
                                     or cur.get("knowledgeid"))
        all_params["uuid"] = uuid
        all_params["qrcEnc"] = qr_params.get("qrcEnc") or qr_params.get("enc") or ""

        self.log(f"参数: courseid={all_params.get('courseid')} "
                 f"clazzid={all_params.get('clazzid')} "
                 f"uuid={all_params.get('uuid')} "
                 f"qrcEnc={all_params.get('qrcEnc')}")
        return all_params

    # ---------------------------------------------------------- 图片处理
    def process_image(self, img_bytes: bytes) -> bytes:
        """
        复刻 JS 中的扰动逻辑：
          1. 随机像素 RGB 各通道 ±10 扰动（最多 200 个点）
          2. 随机黑白噪点（最多 50 个）
          3. 整体亮度 ±5 微调
        """
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        arr = np.array(img, dtype=np.int32)
        h, w = arr.shape[:2]

        # 1) 随机像素扰动
        perturbation_count = int(min(200, arr.size / 50))
        for _ in range(perturbation_count):
            y = random.randrange(h)
            x = random.randrange(w)
            for c in range(3):
                delta = random.randint(-10, 10)
                arr[y, x, c] = max(0, min(255, arr[y, x, c] + delta))

        # 2) 黑白噪点
        noise_count = int(min(50, w * h / 1000))
        for _ in range(noise_count):
            y = random.randrange(h)
            x = random.randrange(w)
            b = 255 if random.random() > 0.5 else 0
            arr[y, x, 0] = arr[y, x, 1] = arr[y, x, 2] = b

        # 3) 整体亮度微调
        bright = random.randint(-5, 5)
        arr = np.clip(arr + bright, 0, 255).astype(np.uint8)

        out = Image.fromarray(arr, "RGB")
        buf = BytesIO()
        out.save(buf, format="JPEG", quality=80)
        self.log("图片扰动处理完成")
        return buf.getvalue()

    # ------------------------------------------------------- 请求各接口
    def get_user_token(self) -> str:
        """获取上传用 _token"""
        url = "https://pan-yz.chaoxing.com/api/token/uservalid"
        r = self.http.get(url, headers=self._headers(), timeout=15)
        r.raise_for_status()
        data = r.json()
        token = data.get("_token")
        if not token:
            raise RuntimeError(f"获取 token 失败: {data}")
        self.log(f"获取上传 token 成功: {token[:16]}...")
        return token

    def get_user_face_image(self, puid: str) -> bytes:
        """获取本人已注册的人脸图片二进制数据"""
        url = "https://passport2-api.chaoxing.com/api/getUserFaceid"
        enc = hashlib.md5((puid + self.FACE_ENC_SALT).encode("utf-8")).hexdigest()
        params = {
            "enc": enc,
            "token": self.FACE_API_TOKEN,
            "_time": int(time.time() * 1000),
        }
        signed = self.add_inf_enc_sign(params)

        r = self.http.get(url, params=signed, headers=self._headers(), timeout=15)
        r.raise_for_status()
        data = r.json()

        if data.get("result") != 1:
            raise RuntimeError(f"获取人脸图片 URL 失败: {data}")

        http_url = (data.get("data") or {}).get("http")
        if not http_url:
            raise RuntimeError(f"响应中未包含人脸图片 URL: {data}")

        self.log(f"人脸图片 URL: {http_url}")
        r2 = self.http.get(http_url, headers=self._headers(), timeout=20)
        r2.raise_for_status()
        self.log(f"获取人脸图片成功，{len(r2.content)} 字节")
        return r2.content

    def upload_face_image(self, img_bytes: bytes, puid: str,
                          upload_token: str) -> str:
        """上传处理后的图片，返回 objectId"""
        url = (f"https://pan-yz.chaoxing.com/upload"
               f"?uploadtype=face&_token={upload_token}")
        files = {"file": (f"{puid}.jpg", img_bytes, "image/jpeg")}
        data = {"puid": puid}

        r = self.http.post(url, files=files, data=data,
                           headers=self._headers(), timeout=30)
        r.raise_for_status()
        j = r.json()
        obj_id = j.get("objectId")
        if not obj_id:
            raise RuntimeError(f"上传失败: {j}")
        self.log(f"图片上传成功 objectId={obj_id}")
        return obj_id

    # ------------------------------------------------------- 提交识别
    def _do_submit(self, params: dict, object_id: str) -> dict:
        """单次提交，返回 {'status': success|retry|fatal}"""
        url = ("https://mooc1-api.chaoxing.com/mooc-ans/qr/updateqrstatus"
               f"?uuid2={params.get('uuid', '')}"
               f"&clazzId2={params.get('clazzid', '')}")

        fields = [
            ("clazzId",               params.get("clazzid") or ""),
            ("courseId",              params.get("courseid") or ""),
            ("uuid",                  params.get("uuid") or ""),
            ("qrcEnc",                params.get("qrcEnc") or ""),
            ("cpi",                   params.get("cpi") or ""),
            ("liveDetectionStatus",   "1"),
            ("objectId",              object_id),
            ("knowledgeid",           params.get("knowledgeid") or "0"),
            ("signt",                 params.get("signt") or ""),
            ("signk",                 params.get("signk") or ""),
            ("cxtime",                params.get("cxtime") or ""),
            ("cxcid",                 params.get("cxcid") or ""),
            ("videojobid",            params.get("videojobid") or ""),
            ("videoCollectTime",      params.get("realCollectTime") or "0"),
            ("chaptervideoobjectid",  params.get("chaptervideoobjectid") or ""),
        ]
        # 用 multipart/form-data 提交（等价于 JS 的 FormData）
        files = [(k, (None, v)) for k, v in fields]

        headers = self._headers({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        })

        try:
            r = self.http.post(url, files=files, headers=headers, timeout=20)
        except Exception as e:
            self.log(f"提交请求异常: {e}", "ERROR")
            return {"status": "retry"}

        # 解析响应
        try:
            data = r.json()
        except Exception:
            if "网页解析失败" in (r.text or ""):
                self.log("服务器返回『网页解析失败』，URL 或参数可能不对", "ERROR")
                return {"status": "fatal"}
            self.log(f"响应非 JSON: {r.text[:200]}", "ERROR")
            return {"status": "retry"}

        self.log(f"提交响应: {data}")

        code = data.get("code")
        msg = data.get("msg") or data.get("message")
        ok = data.get("status")

        if code == 0 and ok is True and msg == "通过":
            self.log("✅ 人脸验证通过！", "INFO")
            return {"status": "success"}

        if code == -4:
            self.log(f"❌ 权限不足: {msg}", "ERROR")
            return {"status": "fatal"}

        if msg == "二维码已失效，请刷新后重试":
            self.log("❌ 二维码已失效，请刷新页面", "ERROR")
            return {"status": "fatal"}

        self.log(f"⚠️ 提交未通过: {msg}", "WARN")
        return {"status": "retry"}

    def submit_sign(self, params: dict, object_id: str) -> bool:
        """
        提交人脸识别，失败时重新获取 token / 图片 / objectId 再重试
        """
        retry = 0
        while retry <= self.MAX_RETRIES:
            result = self._do_submit(params, object_id)
            if result["status"] == "success":
                return True
            if result["status"] == "fatal":
                return False

            retry += 1
            if retry > self.MAX_RETRIES:
                self.log("已达最大重试次数，放弃", "ERROR")
                return False

            self.log(f"{self.RETRY_DELAY}s 后进行第 {retry} 次重试（重新取图）...")
            time.sleep(self.RETRY_DELAY)

            try:
                puid = self.get_uid()
                if not puid:
                    raise RuntimeError("未获取到 _uid")
                upload_token = self.get_user_token()
                raw = self.get_user_face_image(puid)
                processed = self.process_image(raw)
                object_id = self.upload_face_image(processed, puid, upload_token)
            except Exception as e:
                self.log(f"重试准备阶段失败: {e}", "ERROR")
        return False

    # ------------------------------------------------------- 主流程
    def run(self) -> bool:
        """完整流程：取参数 → 取 token → 取图 → 处理 → 上传 → 提交"""
        if self.is_processing:
            self.log("正在处理中，跳过本次调用")
            return False

        self.is_processing = True
        try:
            puid = self.get_uid()
            if not puid:
                raise RuntimeError("未获取到 _uid，请先登录超星")

            # 1. 提取参数
            params = self.get_all_params(force=True)
            if not params:
                self.log("首次提取失败，2s 后重试...")
                time.sleep(2)
                params = self.get_all_params(force=True)
            if not params:
                raise RuntimeError("未能提取到有效 QR 参数")

            missing = [k for k in ("courseid", "clazzid", "cpi", "uuid")
                       if not params.get(k)]
            if missing:
                raise RuntimeError(f"缺少必要参数: {', '.join(missing)}")

            # 2. 取 token
            self.log("获取上传 token...")
            upload_token = self.get_user_token()

            # 3. 取人脸图片
            self.log("获取人脸图片...")
            img_bytes = self.get_user_face_image(puid)

            # 4. 图片扰动处理
            self.log("处理人脸图片...")
            processed = self.process_image(img_bytes)

            # 5. 上传
            self.log("上传人脸图片...")
            object_id = self.upload_face_image(processed, puid, upload_token)

            # 6. 提交
            self.log("提交人脸识别...")
            return self.submit_sign(params, object_id)

        except Exception as e:
            self.log(f"处理失败: {e}", "ERROR")
            return False
        finally:
            self.is_processing = False

    # ------------------------------------------------------- 弹窗检测
    def wait_for_face_popup(self, condition=False) -> bool:
        """轮询等待人脸识别弹窗出现"""
        selectors = [
            ".chapterVideoFaceMaskDiv",     # 新版类型 1
            ".maskDiv",                     # 新版类型 2
            ".chapterVideoFaceQrMaskDiv",   # 旧版
        ]
        if condition:
            print("开始检测人脸弹窗", flush=True)
            for sel in selectors:
                try:
                    els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in els:
                        if el.is_displayed():
                            print(f"检测到人脸弹窗: {sel}", flush=True)
                            return True
                except Exception:
                    continue
                time.sleep(0.5)
            print("未检测到人脸弹窗", flush=True)
        return False

def delete_face_popup(driver,pass_face,class_name='maskDiv1 chapterVideoFaceQrMaskDiv'):
    bypass = ChaoxingFaceBypass(driver)
    if bypass.wait_for_face_popup(pass_face):
        print(color.green('正在处理人脸弹窗，请耐心等待'), flush=True)
        ok = bypass.run()
        print(f"[结果] 本次处理: {'成功' if ok else '失败'}", flush=True)
        if ok:
            time.sleep(3)
            return
        else:
            if 'maskDiv1' not in class_name:
                with open(rf'task/tool/face_url.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    face_url = data.get(class_name, '')
                check_face(driver, face_url, course_name=class_name)
                check_face(driver, face_url, face_class='maskDiv', course_name=class_name)
            print(color.green('开始强制删除人脸弹窗'), flush=True)
            try:
                # 等待弹窗容器出现（最长等待10秒）
                popup = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"[class='{class_name}']"))
                )
                # 隐藏弹窗
                # driver.execute_script("arguments[0].style.display='none';", popup)
                driver.execute_script("arguments[0].remove();", popup)
                print(color.green('成功删除人脸弹窗'),flush=True)
            except Exception as e:
                pass
            delete_face_popup(driver,pass_face,'maskDiv1 starttippop faceRecognition_1 chapterVideoFaceMaskDiv')
