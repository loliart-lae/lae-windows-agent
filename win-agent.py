# 主程序
# By Bing_Yanchi From loliart-lae
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from queue import Queue
import argparse, os, yaml, time, json, psutil
import Cmd

# 全局变量
cmdID = 0

Config = {}
resultList = {}

errorTime = []

blockTime = 0

# 清除错误记录
def clear_error():
    global blockTime
    while True:
        clearTime = int(time.time()) - Config['limit']['token']['time']
        if (clearTime in errorTime):
            errorTime.remove(clearTime)
        time.sleep(1)

# 读取配置文件
def GetConfig(filename):
    f = open(filename, encoding="utf-8")
    global Config
    Config = yaml.load(f, Loader= yaml.SafeLoader)
    f.close()

# 通讯模块
def run_q():
    while True:
        get_data = q.get()
        print("[DEBUG - 通信] " + get_data)

        try:
            userID = get_data.split('] ')[0].replace('[', '')
            result = get_data.split('] ')[1]
            resultList[userID] = result
        except:
            resultList[userID] = 'Fail'
            print("[DEBUG - 通信] 处理输出分割出错")

class EchoHTTPHandler(BaseHTTPRequestHandler):
    # 返回执行状态
    def sendReturn(self, code):
        JsonCode = {}
        JsonCode['status'] = code

        try:
            text = json.dumps(JsonCode)
            text = text.encode('utf8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(text)
        except:
            print("[DEBUG] 返回 Json 出错")
    # 返回资源占用
    def sendStatus(self):
        JsonCode = {}

        memory = psutil.virtual_memory()
        memory_lv = float(memory.used) / float(memory.total) * 100

        JsonCode['cpu'] = psutil.cpu_percent(interval=2)
        JsonCode['ram'] = round(memory_lv, 2)

        try:
            text = json.dumps(JsonCode)
            text = text.encode('utf8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(text)
        except:
            print("[DEBUG] 返回 Json 出错")
            
    def do_GET(self):
        global blockTime
        state = False

        # 错误冻结检查
        if (int(time.time()) < blockTime):
            print("[WARN] 安全保护, 已阻止一条连接")
            self.sendReturn(0)
            return

        # 语法检查
        if (self.path == "/" or "?" not in self.path or len(self.path.split("?")) != 2): 
            self.sendReturn(0)
            return
        string = self.path.split("?")[1]
        
        # 记录参数
        args = {}
        for key in string.split('&'):
            if "=" in key and len(key.split("=")) == 2:
                if key.split("=")[0] != '' and key.split("=")[1] != '':
                    args[key.split("=")[0]] = key.split("=")[1]
        
        type = self.path.replace("/", "").split("?")[0]
        
        # 检查 token
        if ("token" not in args or args["token"] != Config["token"]):
            # 如果启用安全限制
            if (Config['limit']['token']['fail'] > 0):
                errorTime.append(int(time.time()))
                # 检查是否超出, 超出则冻结
                if (len(errorTime) >= Config['limit']['token']['fail']):
                    blockTime = int(time.time()) + Config['limit']['token']['block']

            self.sendReturn(0)
            return
        
        # 内存检查            
        if (type not in Config['limit']['ram']['pass']):
            memory = psutil.virtual_memory()
            memory_lv = float(memory.used) / float(memory.total) * 100
            if (memory_lv > Config['limit']['ram']['percent']):
                self.sendReturn(0)
                return
        
        global cmdID
        
        # 预设的注销程序
        if (type == "logout"):
            # 如果参数中没有 username
            if ("username" not in args):
                self.sendReturn(0)
                return

            # 运行 CMD
            cmdID += 1
            nowID = cmdID

            self.th_get_id = Thread(target=Cmd.Run, args=(type, "query user " + args["username"], nowID, q))
            self.th_get_id.setDaemon(True)
            self.th_get_id.start()

            # 循环检测结果
            for i in range(0, 30):
                if str(nowID) in resultList:
                    userID = resultList[str(nowID)]
                    del resultList[str(nowID)]
                    
                    if (userID == "Fail"):
                        state = False
                        break
                    else:
                        state = True
                        os.system("logoff " + userID)
                        break
                time.sleep(0.1)
        elif (type == "create"):
            # 如果参数中没有 username
            if ("username" not in args):
                self.sendReturn(0)
                return

            # 运行 CMD
            cmdID += 1
            nowID = cmdID

            self.th_get_users = Thread(target=Cmd.Run, args=("users", "net user", nowID, q))
            self.th_get_users.setDaemon(True)
            self.th_get_users.start()

            # 循环检测结果
            for i in range(0, 30):
                if str(nowID) in resultList:
                    users = resultList[str(nowID)]
                    del resultList[str(nowID)]
                    
                    if (users == "Fail"):
                        self.sendReturn(0)
                        return
                    else:
                        user = users.split(",")

                        if (args["username"] in user):
                            self.sendReturn(0)
                            return
                        else:
                            pass
                time.sleep(0.1)

        # 获取资源状态
        elif (type == "status"):
            self.sendStatus()
            return

        # 根据配置文件执行语句
        if (type in Config):
            for cmd in Config[type]:
                for key in args:
                    cmd = cmd.replace("$" + key, args[key])
                os.system(cmd)
            state = True

        # 返回 Json
        if (state): self.sendReturn(1)
        else: self.sendReturn(0)

# 通信部分    
q = Queue()

if __name__ == '__main__':
    GetConfig('config.yml')
    
    ip = Config["address"]
    port = Config["port"]

    # 启动通信进程
    th_run_q = Thread(target=run_q)
    th_run_q.setDaemon(True)
    th_run_q.start()

    # 启动 token 错误清除
    th_clear_error = Thread(target=clear_error)
    th_clear_error.setDaemon(True)
    th_clear_error.start()
    
    print('Listening %s:%d' % (ip, port))
    server = HTTPServer((ip, port), EchoHTTPHandler)
    server.serve_forever()