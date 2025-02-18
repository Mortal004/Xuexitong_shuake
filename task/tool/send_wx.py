# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import logging
import traceback


def send_error(txt):
    # 配置日志记录
    logging.basicConfig(level=logging.ERROR, filename='error.log', filemode='w',
                        format='%(asctime)s - %(levelname)s: %(message)s',encoding='utf-8')
    logging.error(txt)


if __name__ == '__main__':
    try:
        你好
    except:
        error_msg = traceback.format_exc()
        send_error(error_msg)
