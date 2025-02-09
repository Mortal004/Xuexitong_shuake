"""30m：黑色

31m：红色

32m：绿色

33m：黄色

34m：蓝色

35m：洋红色

36m：青色

37m：白色"""

def red(some_str):
    return '\033[31m'+ some_str +'\033[0m'

def yellow(some_str):
    return '\033[31m' + some_str +'\033[0m'

def blue(some_str):
    return '\033[34m' + some_str +'\033[0m'

def green(some_str):
    return '\033[32m' + some_str +'\033[0m'

def magenta(some_str):
    return '\033[35m'+some_str+'\033[0m'

def black(some_str):
    return '\033[30m' + some_str +'\033[0m'
