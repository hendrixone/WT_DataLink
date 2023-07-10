# WT Datalink

为战雷ASB做的一款开黑软件,通过服务器共享数据实现实时展示队友方位。

原理为访问8111端口并将数据上传至服务器，由服务器广播后本地进行显示

## 效果:

游戏内显示实时队友位置，通过窗口化游戏覆盖的地图形式

画饼：使用类似于真实飞机头显的方式将队友位置标记在屏幕空间上（开发中）

## 框架
可视化：PyQt5
exe打包：pyinstaller

## 使用方法

建议先创建虚拟环境

1.安装依赖
```bash
python -m pip install -r requirements.txt
```

2.修改main.py中的服务器地址

3.运行
```bash
python main.py
```

## 打包

```bash
pyinstaller -F main.spec
```
