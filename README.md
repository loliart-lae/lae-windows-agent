# lae-windows-agent
Win Agent

对应 `Light App Engine` 的 `共享的 Windows` 服务

推荐 Python 版本：`3.6.5` ，不推荐版本 `3.6.10`

### 编译
1. 安装 `Python 3.6.5`
2. 安装 第三方库 `pyyaml` `psutil` `pyinstaller`
3. 运行 `build.cmd`
4. 拷贝 `config.yml` 到 `build\win-agent` 文件夹
5. 运行 `build\win-agent\win-agent.exe` 可执行文件

#### 疑难解答
你有可能遇到的问题，由用户 dnyyfb 整理 [https://f.lightart.top/d/14-lae-windows-agent](https://f.lightart.top/d/14-lae-windows-agent)

### 请求格式

你须要使用 `GET` 访问 `http://address:port/{type}?token={token}&parameter1={parameter1}&parameter2={parameter2}`

其中问号前的内容，是 `config.yml` 中定义的名称。
你还可以在配置文件中使用与访问格式相同名称的参数，来定义执行时的变量。

#### 特殊类型

1. `status` : 获取资源占用
  
  访问示例: 
  ```
  http://address:port/status?token={token}
  ```
  
  返回示例: 
  ```json
  {"cpu": 3.3, "ram": 38.38}
  ```

### 配置文件
此部分过于简单易懂，不做解释
