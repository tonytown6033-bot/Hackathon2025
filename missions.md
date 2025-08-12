# 游戏关卡

### 比赛任务 (Missions)

开发一个 AI Agent，接收用户输入的自然语言指令，在 20 个关卡（暂定）中完成任务目标。每当完成一个关卡，游戏将生成一份加密日志，参赛者需上传该日志至官网用于评分，得分将实时公布在 [Leader boards]() 榜单。


### Log文件
  
完成  

MacOS位于 ： ~/Library/Application Support/OpenRA/Logs  
Windows位于：%APPDATA%\OpenRA\Logs

### 关卡场景

游戏关卡设计的难度有易有难，涵盖多种挑战。不同的关卡反映不同的场景：


- Mission-01 Basic Building  
  - 基础建造
  - Score：100  
- Mission-02 Fog of War
  - 探索地图，达到80%探索度
  - Score：115 - 耗时(second)  
- Mission-03 Advanced Building
  - 建造更多建筑和单位
  - Score: 100
- Mission-04 Air Strike
  - 用Yaks摧毁敌方基地
  - Score: 220 - 5 * lossYaks - 耗时(second)  
- Mission-05 Basic Defense
  - 基础防御
  - Score: 10 + 2 * KilledEnemy  + 50(killedAllEnemy)
- Mission-06 Unit Counter
  - 兵种克制
  - Score: 100 - 10 * LossTank - 5 * LossInfantry
- Mission-07 Advanced Attack
  - 全面进攻
  - Score: 50(DestoryEnemyBase) + 10 * DestoryEnemyPower + 1 * DestoryEnemyUnit - 2 * LossUnit




#### 评分与日志上传

- 游戏自动生成包含关键指标（通关时间、击杀数、战损比等）的加密日志
- 参赛者将日志上传至官网（[link]）
- 组委会根据评估规则评分并更新排名
