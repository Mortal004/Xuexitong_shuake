
"""
解除学习通多端学习监控
原理：
1. 劫持 Element.prototype.appendChild，拦截 detect.chaoxing.com 监控脚本注入
2. 覆盖 window.confirm，自动关闭多端登录提示弹窗
"""

import time
from selenium.webdriver.remote.webdriver import WebDriver

class DisableMonitor:
    """解除多端学习监控"""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._enabled = False
        self._confirm_interval_script = None

    def enable(self):
        """开启多端学习（解除监控）"""
        if self._enabled:
            return
        # ============ 手段二：覆盖 confirm 和 alert 弹窗 ============
        self.driver.execute_script("""
                // 覆盖 confirm，永远返回 true（自动点击确定）
                window._originalConfirm = window.confirm;
                window.confirm = function(msg) {
                    console.log('[多端学习] 已自动关闭 confirm 弹窗:', msg);
                    return true;
                };

                // 覆盖 alert，静默关闭（无返回值）
                window._originalAlert = window.alert;
                window.alert = function(msg) {
                    console.log('[多端学习] 已自动关闭 alert 弹窗:', msg);
                    // 不执行任何操作，弹窗消失
                };
            """)
        # ============ 手段一：劫持 appendChild，拦截监控脚本 ============
        self.driver.execute_script("""
            // 保存原始 appendChild
            if (!window._originalAppendChild) {
                window._originalAppendChild = Element.prototype.appendChild;
            }

            Element.prototype.appendChild = function() {
                try {
                    // 拦截 detect.chaoxing.com 的监控脚本
                    if (arguments[0].src && arguments[0].src.indexOf('detect.chaoxing.com') > 0) {
                        console.log('[多端学习] 已拦截监控脚本:', arguments[0].src);
                        return;  // 不注入
                    }
                } catch (e) {}
                // 正常脚本放行
                return window._originalAppendChild.apply(this, arguments);
            };
        """)



        # ============ 手段三：定时重新覆盖（防止页面恢复） ============
        self._confirm_interval_script = """
            if (!window._confirmInterval) {
                window._confirmInterval = setInterval(function() {
                    window.confirm = function(msg) { 
                        console.log('[多端学习] 定时重设 confirm:', msg);
                        return true; 
                    };
                    window.alert = function(msg) {
                        console.log('[多端学习] 定时重设 alert:', msg);
                    };
                }, 2000);
            }
        """
        self.driver.execute_script(self._confirm_interval_script)

        self._enabled = True
        print('[多端学习] 监控已解除，可以多端同时学习，且已自动屏蔽 alert/confirm 弹窗')

    def disable(self):
        """关闭多端学习（恢复监控）"""
        if not self._enabled:
            return

        self.driver.execute_script("""
            // 恢复原始 appendChild
            if (window._originalAppendChild) {
                Element.prototype.appendChild = window._originalAppendChild;
            }

            // 恢复原始 confirm
            if (window._originalConfirm) {
                window.confirm = window._originalConfirm;
            }

            // 清除定时器
            if (window._confirmInterval) {
                clearInterval(window._confirmInterval);
                window._confirmInterval = null;
            }
        """)

        self._enabled = False
        print('[多端学习] 监控已恢复')

    def is_enabled(self) -> bool:
        """检查是否已开启"""
        return self._enabled

# ============ 使用示例 ============
if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.edge.options import Options

    options = Options()
    driver = webdriver.Edge(options=options)

    # 先登录学习通...
    driver.get('https://i.chaoxing.com/')

    # 开启多端学习
    monitor = DisableMonitor(driver)
    monitor.enable()
    time.sleep(1000)

    # ... 后续正常刷课 ...

    # 关闭多端学习
    # monitor.disable()