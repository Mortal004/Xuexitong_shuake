# 一、项目概述
这个脚本旨在帮助用户在学习通平台上自动刷课和刷题（仅选择题和判断题且答案准确性不保证）。它主要利用selenium库进行网页自动化操作，pyautogui库辅助一些鼠标和键盘操作，tkinter库创建可视化的设置窗口。
# 二、安装指南
1. 依赖库安装
  1.确保已经安装了selenium、pyautogui、tkinter库、colorama库。
      1.对于selenium：
          1.如果使用pip，可以通过pip install selenium命令安装。
      2.pyautogui安装：
          1.使用pip install pyautogui进行安装。
      3.tkinter：
          1.在大多数Python安装中，tkinter是自带的，如果没有，可以根据操作系统进行相应安装。
     4.colorama库：
         使用pip install coolorama进行安装
3. 谷歌驱动（ChromeDriver）
  1.需要自行下载与你使用的谷歌浏览器版本一致的谷歌驱动（ChromeDriver）。下载地址：ChromeDriver官方下载页面。
4. 搜题插件
  1.搜题插件已经包含在源代码文件中，文件后缀为.crx。
# 三、使用示例
1. 运行脚本
  1.运行start.py脚本，将会弹出一个tkinter创建的窗口。
2. 配置信息
  1.在弹出的设置窗口中：
      1.填写谷歌驱动的地址，例如：C:/chromedriver/chromedriver.exe。
      2.填写搜题插件的地址，例如：[脚本所在目录]/搜题插件.crx。
      3.输入你的学习通账号和密码。
      4.输入要刷的课程名称。
      5.选择是否要刷题（如果选择刷题，请注意后续扫码登录步骤）。
3. 启动程序
  1.如果选择刷题：
      1.点击启动程序后，需要先用大学生搜题酱进行扫码登录。
  2.如果不刷题：
      1.直接点击启动程序即可开始刷课。
4. 教程
   [完整使用教程](https://v.douyin.com/if1cV9ba/)
# 四、功能介绍
  1.刷课功能：根据用户输入的课程名称，自动在学习通平台上执行刷课相关操作，模拟用户观看课程的行为。
  2.刷题功能（仅选择题和判断题）：在用户选择刷题并且成功扫码登录（如果需要）后，会尝试对课程中的选择题和判断题进行作答，但答案不保证完全正确。
# 五、贡献指南
1. 问题报告
  1.若在使用过程中遇到任何问题，如程序崩溃、无法正常刷课刷题等，请在项目的GitHub Issues页面创建新的问题。
  2.在报告问题时，请详细描述问题发生的情况，包括但不限于错误提示信息、操作步骤、配置信息等。
2. 代码贡献
  1.如果您想要对这个脚本进行改进或添加新功能：
      1.Fork本项目到自己的GitHub账号（如果有）。
      2.创建一个新的分支，分支名称建议按照[功能名称]-[简要描述]的格式，如quiz - fix - answer - accuracy。
      3.在本地进行代码修改并测试。
      4.确保您的代码遵循项目原有的代码风格（如果有）。
      5.提交代码并编写清晰的提交信息，包括修改的目的、内容以及可能影响的部分。
      6.在自己的GitHub仓库中创建Pull Request，详细说明您所做的修改以及对项目的贡献。
# 六、声明
  1.本脚本仅供学习和研究目的使用，使用本脚本进行学习通刷课刷题可能违反学习通平台的使用条款。
  2.用户需自行承担使用本脚本所带来的一切风险，包括但不限于账号封禁等风险。
  3.开发者不对因使用本脚本导致的任何问题负责。
  4.本项目只供对编程感兴趣、喜欢研究的同学来学习和锻炼自己的能力。
  5.本项目禁止进行任何商业化
# 我的 GitHub 统计
 
[![Anurag's GitHub stats](https://github-readme-stats.vercel.app/api?username=Mortal004)](https://github.com/anuraghazra/github-readme-stats)
 
[![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=Mortal004&layout=compact)](https://github.com/anuraghazra/github-readme-stats)
