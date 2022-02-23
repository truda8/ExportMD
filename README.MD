# ExportMD-rectify-pics
![Version](https://img.shields.io/badge/Version-1.0.0-blue) ![License](https://img.shields.io/badge/license-MIT-yellow) ![python](https://img.shields.io/badge/python->=3.6-orange)

简介：ExportMD语雀知识库自动导出为 Markdown 格式，支持同时导出多个知识库。
但ExportMD导出连续三张图片时，会出现错误，只有第一张图片的内容会被识别，本复刻版本增加了正则表达式，修复这一情况

## 安装
### 环境要求
 - python >= 3.6

### 安装 python 依赖
```bash
pip install -r requirements.txt
```

## 使用
### 使用 python3 运行
```bash
python ExportMD.py
```

## 获取 namespace
知识库 namespace：知识库 URL 中路径部分

知识库 [https://www.yuque.com/YourYuqueUserName](https://www.yuque.com/YourYuqueUserName)  对应的 *namespace* 为 *YourYuqueUserName*

## 获取 token
![token](https://s3.jpg.cm/2021/08/17/IUIASp.png)
