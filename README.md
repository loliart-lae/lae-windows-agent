# lae-windows-agent
Win Agent

### 编译
1. 运行 `build.cmd`
2. 拷贝 `config.yml` 到 `build\win-agent` 文件夹
3. 运行 `build\win-agent\win-agent.exe` 可执行文件

### 请求格式

你须要使用 `GET` 访问 `http://address:port/{type}?token={token}&parameter1={parameter1}&parameter2={parameter2}`

其中问号前的内容，是 `config.yml` 中定义的名称。
你还可以在配置文件中使用与访问格式相同名称的参数，来定义执行时的变量。

### 配置文件
此部分过于简单易懂，不做解释
