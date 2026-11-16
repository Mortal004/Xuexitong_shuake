# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
# -*- coding: utf-8 -*-
"""
邮箱通知模块

能力：
  * 内置常见邮箱服务商的 SMTP 参数与「如何获取授权码」的教程地址；
  * 读取/保存 account_info.json 里的邮箱配置（授权码做 Base64 兜底编码）；
  * 发送纯文本通知：开始刷课、完成一个章节、整门课完成、运行报错。

设计原则：
  * 所有 notify_* 函数都不会抛异常 —— 邮件发不出去绝不能影响刷课；
  * 发送前重新读取配置，这样主程序（子进程）能立刻用上 GUI 里刚保存的设置；
  * 只依赖标准库（smtplib / ssl / email），便于 PyInstaller 打包。
"""
from __future__ import annotations

import base64
import binascii
import json
import re
import socket
import smtplib
import ssl
import time
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formatdate

from core.config_manager import ConfigManager

# ---------------------------------------------------------------- 服务商预设
# ssl=True  -> SMTP_SSL（一般 465）
# ssl=False -> SMTP + STARTTLS（一般 587）
PROVIDERS = {
    'QQ邮箱': {
        'host': 'smtp.qq.com', 'port': 465, 'ssl': True,
        'help': 'https://service.mail.qq.com/detail/0/75',
        'hint': 'QQ邮箱网页版 → 设置 → 账号 → 开启「POP3/IMAP/SMTP/Exchange/CardDAV 服务」'
                '→ 生成授权码（16 位，不是 QQ 登录密码）',
    },
    '163邮箱': {
        'host': 'smtp.163.com', 'port': 465, 'ssl': True,
        'help': 'https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2a5feb28b66796d3b',
        'hint': '163邮箱网页版 → 设置 → POP3/SMTP/IMAP → 开启服务 → 新增「客户端授权密码」',
    },
    '126邮箱': {
        'host': 'smtp.126.com', 'port': 465, 'ssl': True,
        'help': 'https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2a5feb28b66796d3b',
        'hint': '126邮箱网页版 → 设置 → POP3/SMTP/IMAP → 开启服务 → 新增「客户端授权密码」',
    },
    '腾讯企业邮箱': {
        'host': 'smtp.exmail.qq.com', 'port': 465, 'ssl': True,
        'help': 'https://service.exmail.qq.com/',
        'hint': '企业邮箱网页版 → 设置 → 客户端设置 → 开启 IMAP/SMTP → 生成「客户端专用密码」',
    },
    'Gmail': {
        'host': 'smtp.gmail.com', 'port': 587, 'ssl': False,
        'help': 'https://support.google.com/accounts/answer/185833',
        'hint': 'Google 账号 → 安全性 → 开启两步验证 → 生成「应用专用密码」（需能访问 Google）',
    },
    'Outlook': {
        'host': 'smtp.office365.com', 'port': 587, 'ssl': False,
        'help': 'https://support.microsoft.com/zh-cn/account-billing',
        'hint': 'Microsoft 账户 → 安全 → 高级安全选项 → 创建「应用密码」',
    },
    '自定义SMTP': {
        'host': '', 'port': 465, 'ssl': True,
        'help': '',
        'hint': '请自行填写 SMTP 服务器与端口：SSL 一般为 465，STARTTLS 一般为 587',
    },
}

DEFAULT_PROVIDER = 'QQ邮箱'
_ENCODE_PREFIX = 'b64:'


# ---------------------------------------------------------------- 配置读写
def provider_names():
    return list(PROVIDERS.keys())


def provider_info(name):
    return PROVIDERS.get(name, PROVIDERS[DEFAULT_PROVIDER])


def encode_secret(text):
    """授权码落盘前做一次 Base64（防肩窥，不是加密）"""
    text = (text or '').strip()
    if not text:
        return ''
    return _ENCODE_PREFIX + base64.b64encode(text.encode('utf-8')).decode('ascii')


def decode_secret(value):
    value = (value or '').strip()
    if not value:
        return ''
    if value.startswith(_ENCODE_PREFIX):
        try:
            return base64.b64decode(value[len(_ENCODE_PREFIX):]).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError):
            return ''
    # 兼容手工填写明文的情况
    return value


def load_settings():
    """从 account_info.json 读取邮箱配置（授权码已解码）"""
    try:
        cfg = ConfigManager().get_email_config()
    except Exception:
        cfg = {}
    cfg['provider'] = cfg.get('provider') or DEFAULT_PROVIDER
    cfg['auth_code'] = decode_secret(cfg.get('auth_code'))
    return cfg


def save_settings(cfg):
    """保存邮箱配置；auth_code 会自动编码"""
    data = dict(cfg)
    data['auth_code'] = encode_secret(data.get('auth_code'))
    try:
        return ConfigManager().save_email_config(**data)
    except Exception:
        return False


def is_enabled():
    """邮箱通知是否已开启且配置完整"""
    try:
        cfg = load_settings()
        if not int(cfg.get('enabled') or 0):
            return False
        host, _port, _ssl = resolve_server(cfg)
        return bool(host and cfg.get('account') and cfg.get('auth_code'))
    except Exception:
        return False


def resolve_server(cfg):
    """返回 (host, port, use_ssl)。自定义服务商才使用用户填写的地址"""
    info = provider_info(cfg.get('provider'))
    if cfg.get('provider') == '自定义SMTP':
        host = (cfg.get('host') or '').strip()
        port = int(cfg.get('port') or 465)
        use_ssl = bool(int(cfg.get('use_ssl', 1) or 0))
    else:
        host = info['host']
        port = int(info['port'])
        use_ssl = bool(info['ssl'])
    return host, port, use_ssl


# ---------------------------------------------------------------- 发送节流
# 多端模式下每门课一个子进程，会同时调用 notify_start；用一个状态文件做节流，
# 避免一次启动收到好几封"已开始"邮件。某个通知发不出去也不影响主流程。
STATE_PATH = 'task/tool/email_notify_state.json'


def _load_state():
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _save_state(data):
    try:
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except (OSError, PermissionError):
        pass


def _allow(key, interval):
    """同一 key 在 interval 秒内只允许一次"""
    now = time.time()
    data = _load_state()
    try:
        last = float(data.get(key) or 0)
    except (TypeError, ValueError):
        last = 0
    if now - last < interval:
        return False
    data[key] = now
    _save_state(data)
    return True


def _unmark(key):
    """撤销一次节流标记（发送失败时调用，允许稍后重试）"""
    data = _load_state()
    if key in data:
        data.pop(key, None)
        _save_state(data)


# ---------------------------------------------------------------- 发送
def send_mail(subject, body, cfg=None):
    """
    发送一封纯文本邮件。
    Returns:
        (bool, str) —— (是否成功, 说明)
    """
    cfg = cfg or load_settings()
    host = port = None
    try:
        host, port, use_ssl = resolve_server(cfg)
        account = (cfg.get('account') or '').strip()
        auth_code = (cfg.get('auth_code') or '').strip()
        receiver = (cfg.get('receiver') or '').strip() or account

        if not host:
            return False, '未填写 SMTP 服务器地址'
        if not account or '@' not in account:
            return False, '未填写正确的邮箱地址'
        if not auth_code:
            return False, '未填写授权码'

        # 收件人支持用逗号/分号分隔多个
        receivers = [r.strip() for r in re.split(r'[,;，；]', receiver) if r.strip()]
        if not receivers:
            receivers = [account]

        message = MIMEText(body, 'plain', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = account
        message['To'] = ', '.join(receivers)
        message['Date'] = formatdate(localtime=True)

        context = ssl.create_default_context()
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=20, context=context)
        else:
            server = smtplib.SMTP(host, port, timeout=20)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()

        try:
            server.login(account, auth_code)
            server.sendmail(account, receivers, message.as_string())
        finally:
            try:
                server.quit()
            except Exception:
                pass
        return True, f'已发送到 {", ".join(receivers)}'
    except smtplib.SMTPAuthenticationError:
        return False, ('授权码或邮箱地址不正确：请确认已在邮箱设置中开启 SMTP 服务，'
                       '并填写「授权码 / 客户端专用密码」而不是登录密码')
    except smtplib.SMTPSenderRefused:
        return False, '发件人被拒绝：邮箱地址与登录账号不一致，或服务商限制了发件'
    except smtplib.SMTPException as exc:
        return False, f'邮件服务器返回错误：{exc}'
    except socket.timeout:
        return False, f'连接 {host}:{port} 超时，请检查网络或服务器地址'
    except (socket.gaierror, OSError) as exc:
        return False, f'无法连接邮件服务器 {host}:{port}（{exc}）'
    except Exception as exc:                      # 兜底：绝不向上抛
        return False, f'发送失败：{exc}'


def test_connection(cfg):
    """发送一封测试邮件，用于配置界面的「测试」按钮"""
    body = (
        '这是一封来自「学习通刷课」的测试邮件。\n\n'
        '如果你收到了它，说明邮箱通知已经配置成功。\n'
        '之后开始刷课、完成一个章节、以及程序报错时，都会通过这个邮箱提醒你。\n\n'
        f'发送时间：{_now()}\n'
    )
    return send_mail('【学习通刷课】邮箱通知测试', body, cfg)


# ---------------------------------------------------------------- 通知内容
def _now():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def _progress_text(progress):
    if not progress:
        return '未知'
    done, total = progress
    if not total:
        return f'{done}/{total}'
    return f'{done}/{total}（{done / total * 100:.1f}%）'


def _print(ok, message, kind):
    prefix = '已发送' if ok else '发送失败'
    try:
        from task.tool import color
        text = color.green(f'[邮箱] {kind}通知{prefix}：{message}') if ok \
            else color.red(f'[邮箱] {kind}通知{prefix}：{message}')
    except Exception:
        text = f'[邮箱] {kind}通知{prefix}：{message}'
    try:
        print(text, flush=True)
    except Exception:
        pass


def notify_start(courses, task_type='章节'):
    """开始刷课时提醒"""
    try:
        cfg = load_settings()
        if not int(cfg.get('enabled') or 0):
            return False
        if not _allow('start', 60):
            return False
        course_text = '\n'.join(f'  {i}. {name}' for i, name in enumerate(courses or [], 1)) or '  （未选择）'
        body = (
            '学习通刷课已开始运行。\n\n'
            f'任务类型：{task_type}\n'
            f'课程数量：{len(courses or [])}\n'
            f'课程列表：\n{course_text}\n\n'
            f'开始时间：{_now()}\n\n'
            '完成一个章节后还会再发邮件告知进度。'
        )
        ok, msg = send_mail('【学习通刷课】已开始刷课', body, cfg)
        if not ok:
            _unmark('start')            # 发送失败则允许下次重试
        _print(ok, msg, '开始')
        return ok
    except Exception:
        return False


def notify_chapter(course_name, chapter, task_done, task_total, progress=None, section=''):
    """完成一个章节（本章最后一节结束）时提醒"""
    try:
        cfg = load_settings()
        if not int(cfg.get('enabled') or 0):
            return False
        section_line = f'完成小节：{section}\n' if section else ''
        body = (
            '已完成一个章节。\n\n'
            f'课程名称：{course_name}\n'
            f'章节名称：{chapter}\n'
            f'{section_line}'
            f'本章任务点：{task_done}/{task_total} 完成\n'
            f'课程进度：{_progress_text(progress)}\n'
            f'完成时间：{_now()}\n'
        )
        ok, msg = send_mail(f'【学习通刷课】已完成章节：{chapter}', body, cfg)
        _print(ok, msg, '完成章节')
        return ok
    except Exception:
        return False


# 兼容旧调用名
def notify_section(course_name, chapter, task_done, task_total, progress=None):
    return notify_chapter(course_name, chapter, task_done, task_total, progress)


def notify_course_done(course_name, progress=None):
    """整门课程的任务点全部完成时提醒（附加能力）"""
    try:
        cfg = load_settings()
        if not int(cfg.get('enabled') or 0):
            return False
        body = (
            '本门课程已全部完成。\n\n'
            f'课程名称：{course_name}\n'
            f'课程进度：{_progress_text(progress)}\n'
            f'完成时间：{_now()}\n'
        )
        ok, msg = send_mail(f'【学习通刷课】课程已完成：{course_name}', body, cfg)
        _print(ok, msg, '课程完成')
        return ok
    except Exception:
        return False


# 同一进程内同类型错误只发一封（多端模式每个课程一个进程，互不影响）
_sent_errors = set()


def notify_error(title, detail='', context=''):
    """运行出错时提醒（detail 通常是 traceback，context 可写课程名）"""
    try:
        cfg = load_settings()
        if not int(cfg.get('enabled') or 0):
            return False
        # 注意：这里不做跨进程节流。多端模式下多门课同时刷，
        # 每门课报错都应该各自提醒，不能被别的课程的报错挡掉。
        key = (title, context)
        if key in _sent_errors:
            return False
        _sent_errors.add(key)
        detail = (detail or '').strip()
        if len(detail) > 4000:
            detail = detail[:2000] + '\n...(中间省略)...\n' + detail[-1500:]
        context_line = f'课程：{context}\n' if context else ''
        body = (
            '刷课过程中出现异常，程序已停止或跳过当前任务。\n\n'
            f'错误类型：{title}\n'
            f'{context_line}'
            f'发生时间：{_now()}\n\n'
            '详细信息：\n'
            '----------------------------------------\n'
            f'{detail or "（无详细信息）"}\n'
            '----------------------------------------\n\n'
            '如果反复出现，可以查看程序目录下的 error.log。'
        )
        ok, msg = send_mail(f'【学习通刷课】运行出错：{title}', body, cfg)
        if not ok:
            _sent_errors.discard(key)   # 发送失败允许重试
        _print(ok, msg, '报错')
        return ok
    except Exception:
        return False
