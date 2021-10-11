# Bing_Yanchi
# 主程序
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from queue import Queue
import os, yaml, time, json, psutil
import Cmd

# 全局变量
cmdID = 0

Config = {}
resultList = {}

errorTime = []

# 清除错误记录
def clear_error():
    while True:
        if (int(time.time()) - 60 in errorTime):
            errorTime.remove(int(time.time()) - 60)
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
    def sendstatus(self):
        JsonCode = {}
        JsonCode['cpu'] = psutil.virtual_memory().percent
        JsonCode['ram'] = psutil.cpu_percent()

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
        state = False

        # 错误冻结检查
        if (len(errorTime) >= 10):
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
            errorTime.append(int(time.time()))
            self.sendReturn(0)
            return
        
        # 内存检查
        whitelist =['logout', 'status']
        
        if (type not in whitelist):
            if (psutil.virtual_memory().percent > 90):
                self.sendReturn(0)
                return
        
        # 预设的注销程序
        if (type == "logout"):
            # 如果参数中没有 username
            if ("username" not in args):
                self.sendReturn(0)
                return

            # 运行 CMD
            global cmdID
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
        # 获取资源状态
        elif (type == "status"):
            self.sendstatus()
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