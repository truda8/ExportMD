# ExportMD-rectify-pics
![Version](https://img.shields.io/badge/Version-1.0.0-blue) ![License](https://img.shields.io/badge/license-MIT-yellow) ![python](https://img.shields.io/badge/python->=3.6-orange)

简介：ExportMD语雀知识库自动导出为 Markdown 格式，支持同时导出多个知识库。
但ExportMD导出连续三张图片时，会出现错误，只有第一张图片的内容会被识别，本复刻版本增加了正则表达式，修复这一情况
## 版本v1.0
API导出连着的图片时，会出现很多`<br />`，这时连续图片中只有第一张图片会被识别
```
![image.png](https://cdn.nlark.com/xxx1.png)<br />![image.png](https://cdn.nlark.com/xxx2.png)<br />![image.png](https://cdn.nlark.com/xxx3.png)

```
为了解决这一问题，在原来的ExportMD基础上，我增加了正则表达式，现在连续图片的导出已经没有问题
这里特别感谢ExportMD！
## 版本v1.1
实际使用的时候有遇到一些小问题，主要是接口限制等会导致有时候请求失败
这里使用@stone0090的解决方案，https://github.com/stone0090/ExportMD-rectify-pics/blob/bf2b79ef0afaffcad78253cafa1760f45359623e/ExportMD.py#L198
修改为同步导出，且每次导出等待100ms
本人技术水平，感谢`stone0090`!的修复
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
