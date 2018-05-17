import os
import re,datetime

apk = input("请输入apk包的绝对路径：")
apk_parent_path = os.path.dirname(apk)      #apk包所在的上级目录

#查找adb的所在路径
adbPath = ""
if "ANDROID_HOME" in os.environ:
    rootDir = os.path.join(os.environ["ANDROID_HOME"], "platform-tools")
    for path, subdir, files in os.walk(rootDir):
        if "adb" in files:
            adbPath = os.path.join(path, "adb")
            break
if adbPath == "":
    print("ANDROID_HOME not exist,please install it.")
    exit()

#查找aapt的所在路径
aapt = ""
if "ANDROID_HOME" in os.environ:
    rootDir = os.path.join(os.environ["ANDROID_HOME"], "build-tools")
    for path, subdir, files in os.walk(rootDir):
        if "aapt" in files:
            aapt = os.path.join(path, "aapt")
            break
if aapt == "":
    print("ANDROID_HOME not exist,please install it.")
    exit()

#aapt查看apk包的包名
def get_apk_name(commond):
    p = os.popen(commond)
    r = p.readlines()
    return re.findall(r"name='(.+?)\'", r[0])

commond = aapt+' dump badging '+apk + ' | grep package:'
package = get_apk_name(commond)


def run_monkey(adbPath, package, apk_parent_path):
    log = "monkey.log"  # 存monkey日志于apk的同个目录下
    # 自定义monkey命令
    operation = input("请输入monkey的参数,如–-throttle 100 –-pct-touch 50 –-pct-motion 50 –v –v 1000")

    # 执行monkey
    monkeycmd = adbPath + ' shell monkey -p ' + package[0] + ' ' + operation + ' >' + apk_parent_path + "/" + log
    print(monkeycmd)
    str4 = '.*Error.*'
    os.popen(monkeycmd)

    # 读取monkey日志
    with open(apk_parent_path + "/monkey.log", "r") as file1:
        content = file1.readlines()

    # 将4种日志信息保存到report文件中
    with open(apk_parent_path + "/report.log", "a") as file2:
        file2.write(str(datetime.datetime.now()) + '\n')
        str1 = '.*ANR.*'
        str2 = '.*CRASH.*'
        str3 = '.*Exception.*'
        str4 = '.*finished.*'
        Acount, Ccount, Ecount = 0, 0, 0
        for i in content:
            if re.match(str1, i):
                print('测试过程中出现程序无响应')
                file2.write(i)
                Acount += 1
            elif re.match(str2, i):
                print('测试过程中出现程序崩溃')
                file2.write(i)
                Ccount += 1
            elif re.match(str3, i):
                print('测试过程中出现程序异常')
                file2.write(i)
                Ecount += 1
        if Acount or Ccount or Ecount == 0:
            for i in content:
                if re.match(str4, i):
                    print('测试过程中正常')
                    file2.write(i)
        print('稍后可查看报告：')
        print('位置：', apk_parent_path + '/report.log')

#安装apk包
string = adbPath+' install '  + "\""+ apk + "\""
uninstall = adbPath+' uninstall '  + "\""+ package[0] + "\""
apkinstall = os.popen(string)
print("正在安装apk包......")
str0 = '.*INSTALL_FAILED_ALREADY_EXISTS.*'
str00 = 'Success'
Failure = '.*Failure.*'
info = apkinstall.readlines()  #读取命令行的输出到一个list
for line in info:  #按行遍历
    line = line.strip('\r\n')
    print(line)
    if re.match(str0, line):
        print("apk包已存在，现在删除重新安装,请等待安装完毕")
        os.popen(uninstall)
        apkreinstall = os.popen(string)
        info0 = apkreinstall.readlines()  # 读取命令行的输出到一个list
        for line0 in info0:  # 按行遍历
            line0 = line0.strip('\r\n')
            print(line0)
            if re.match(str00, line0):
                run_monkey(adbPath, package, apk_parent_path)
            elif re.match(Failure,line0):
                print('安装失败，请再次检查')
                exit()
    elif re.match(str00, line):
        run_monkey(adbPath, package, apk_parent_path)
