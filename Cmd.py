# 指令执行
# 根据通道返回内容
# By Bing_Yanchi From loliart-lae

import subprocess

class CmdGo:

    def __init__(self, type, shell, id, out_q):

        self.p = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE)

        self.send = public_channel_client(out_q)

        results = []

        for line in iter(self.p.stdout.readline, b''):
            line = line.strip().decode("GB2312")
            results.append(line)
            print(line)
        
        if (type == "logout"):
            if (len(results) < 2):
                self.send.run("[{}] Fail".format(id))
            else:
                info = []
                for contents in results[1].split():
                    if contents != '' and contents != ' ':
                        info.append(contents)

                if (len(info) == 7):
                    userID = info[2]
                elif (len(info) == 6):
                    userID = info[1]
                else:
                    userID = "Fail"

                self.send.run("[{}] {}".format(id, userID))
        elif (type == "users"):
            if (len(results) < 4):
                self.send.run("[{}] Fail".format(id))
            else:
                info = []

                del(results[-2])

                write = False
                for result in results:
                    if (write == False and result.find('---------------------') != -1):
                        write = True
                    elif (write == True):
                        for contents in result.split():
                            if contents != '' and contents != ' ':
                                info.append(contents)
                
                self.send.run("[{}] {}".format(id, ','.join(info)))
# 通信部分
class public_channel_client(object):
    def __init__(self, out_q):
        self.q = out_q

    def run(self, data):
        self.q.put(data)

def Run(type, shell, nowID, out_q):
    CmdGo(type, shell, nowID, out_q)