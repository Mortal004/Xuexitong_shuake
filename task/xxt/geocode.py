# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
# -*- coding: utf-8 -*-
"""地址 -> 坐标 (高德地理编码)。仅当活动 content 里没有经纬度时使用。"""
from __future__ import annotations

from typing import Optional, Tuple

from . import constants

import requests


def geocode(address: str, timeout: int = 8):
    """
    调用接口盒子API将中文地址转换为经纬度。
    支持模糊查询，并返回结果的准确度评分(score)。
    """
    url = "https://cn.apihz.cn/api/other/jwjuhe.php"
    params = {
        "id": constants.ID,
        "key": constants.DEFAULT_AMAP_KEY,
        "address": address
    }

    try:
        # 推荐使用POST，对中文更友好
        response = requests.post(url, data=params, timeout=timeout)
        response.raise_for_status()  # 检查HTTP错误
        data = response.json()

        if data.get("code") == 200:
            lng = data.get("lng")
            lat = data.get("lat")
            score = data.get("score", 0)
            level = data.get("level", "未知")

            print(f"地址 '{address}' 解析成功:")
            print(f"  坐标: ({lat}, {lng})")
            print(f"  准确度评分: {score}/100 (等级: {level})")

            # 官方建议：score ≥ 70 时结果可信
            if score < 70:
                print("  ⚠️ 注意：准确度评分较低，建议人工核实。")
                # 你可以选择在这里返回 None 或一个标志位，取决于你的业务逻辑

            return float(lat), float(lng)
        else:
            print(f"解析失败 (code={data.get('code')}): {data.get('msg')}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"网络请求出错: {e}")
        return None, None
    except (KeyError, ValueError) as e:
        print(f"解析响应数据出错: {e}, 原始响应: {response.text}")
        return None, None

