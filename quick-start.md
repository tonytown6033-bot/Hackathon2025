# **Quick Start** 

## 环境要求

---

### dotnet x64 6.0的安装

无论在Windows、Linux (Ubuntu) 或 macOS环境下，OpenRA游戏引擎需要安装 x64 版本的dotnet x64 6.0。

https://dotnet.microsoft.com/en-us/download/dotnet/6.0

### Windows系统

如果选择从编译源码开始完成游戏引擎的安装和运行，需要安装vs或vsc和C#相关内容。

如果选择安装发行版（Release Version)，请忽略此步骤。

### Linux系统 (Ubuntu)

如果选择从编译源码开始完成游戏引擎的安装和运行，需要安装vsc和C#相关内容后，通过vsc启动。

如果选择安装发行版（Release Version)，请忽略此步骤。

### macOS系统

如果您的系统未安装brew, 请安装：

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

M 系列芯片MacOS需要安装rosetta

`/usr/sbin/softwareupdate --install-rosetta --agree-to-license`

## OPENRA游戏引擎的下载和安装

---

### Windows系统

```bash
git clone https://github.com/OpenRA-CopilotTestGroup/OpenRA.git
cd OpenRA
# 如果网速不佳，先用cdn store一下，也可以挂代理。无网速问题的开发者请忽略以下这一行
dotnet restore --source https://nuget.cdn.azure.cn/v3/index.json
dotnet build
.\launch-game.cmd Game.Mod=copilot
```

### Linux系统

```bash
git clone https://github.com/OpenRA-CopilotTestGroup/OpenRA.git
cd OpenRA
# 如果网速不佳，先用cdn store一下，也可以挂代理。无网速问题的开发者请忽略以下这一行
dotnet restore --source https://nuget.cdn.azure.cn/v3/index.json
dotnet build
export PATH="/usr/local/share/dotnet/x64:$PATH"
./launch-game.sh Game.Mod=copilot
```

### macOS系统

```bash
git clone https://github.com/OpenRA-CopilotTestGroup/OpenRA.git
cd OpenRA
# 如果网速不佳，先用cdn store一下，也可以挂代理。无网速问题的开发者请忽略以下这一行
dotnet restore --source https://nuget.cdn.azure.cn/v3/index.json
dotnet build
export PATH="/usr/local/share/dotnet/x64:$PATH"
./launch-game.sh Game.Mod=copilot
```



### 游戏引擎的编译

## 游戏关卡

---

在比赛中，我们设计了一些游戏关卡，用于您测试您的AI-Agent完成任务的能力，有简单的任务比如：



## 运行OpenRA游戏引擎

---

### Windows系统

### Linux系统

### macOS系统

##             2.     **运行OpenRA游戏，开一关**

我们打开OpenRA进入战斗关卡

OpenRA在一局游戏进入世界后，会用**socket**，监听**7445**端口**TCP**协议，**UTF-8** **json**格式的报文

可以通过发送和接受这些json格式的报文，查询游戏状态信息，也就是俗称的使用API

以下是一个展开基地车的示例代码，运行游戏后，执行下面的代码可以发送一个展开基地车的指令，展开你的基地车

```
import socket
import json
import uuid
 
payload = {
    "apiVersion": "1.0",
    "requestId": str(uuid.uuid4()),
    "command": "deploy",
    "params": {
        "targets": {
            "type": ["基地车"],
            "faction": "己方"
        }
    },
    "language": "zh"
}
 
data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
 
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", 7445))
    s.sendall(data)
 
```

各种各样的API就是你的操作

可以看文章《OpenRA-API》，介绍了更多丰富的API

你可以使用这些API，提出疑问，缺失



不是很了解socket操作？可以问问各种AI们！

RESTFUL的http格式的API**

专门给Claude等AI使用的**MCP结构的API**

目前这些还在编写中

##             3.     **实现一个AI-Agent**

刚刚我们成功的调用了API，但是人肉调用可是不行的呢？

有没有什么办法让AI来调用API玩游戏

 

简单来说，需要实现一个拥有**感知**和**下令**的Agent

将 模糊的指令 转换为 实际的游戏操作

 

可以看看著名的开源项目 browser-use

https://github.com/browser-use/browser-use

这是一个使用浏览器的Agent，可以帮你自动完成浏览器相关任务 。

## 许可证

---

本项目采用与 OpenRA 相同的 [GPLv3 许可证](https://github.com/OpenRA-CopilotTestGroup/OpenRA/blob/code_gen_test/LICENSE)。

 