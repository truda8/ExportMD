# -*- coding: UTF-8 -*-
# -----------------------------------------
# createTime : 2021-08-17
# author     : Truda
# email      : truda8@pm.me
# description: 自动导出语雀知识库为Markdown格式
# -----------------------------------------

from prettytable import PrettyTable
import re
import os
import aiohttp
import asyncio
from urllib import parse
from PyInquirer import prompt, Separator
from examples import custom_style_2
from colr import color
from cfonts import render, say


class ExportMD:
    def __init__(self):
        self.repo_table = PrettyTable(["知识库ID", "名称"])
        self.namespace, self.Token = self.get_UserInfo()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ExportMD",
            "X-Auth-Token": self.Token
        }
        self.repo = {}
        self.export_dir = './yuque'

    def print_logo(self):
        output = render('ExportMD', colors=['red', 'yellow'], align='center')
        print(output)

    # 语雀用户信息
    def get_UserInfo(self):
        f_name = ".userinfo"
        if os.path.isfile(f_name):
            with open(f_name, encoding="utf-8") as f:
                userinfo = f.read().split("&")
        else:
            namespace = input("请输入语雀namespace：")
            Token = input("请输入语雀Token：")
            userinfo = [namespace, Token]
            with open(f_name, "w") as f:
                f.write(namespace + "&" + Token)
        return userinfo

    # 发送请求
    async def req(self, session, api):
        url = "https://www.yuque.com/api/v2" + api
        # print(url)
        async with session.get(url, headers=self.headers) as resp:
            result = await resp.json()
            return result

    # 获取所有知识库
    async def getRepo(self):
        api = "/users/%s/repos" % self.namespace
        async with aiohttp.ClientSession() as session:
            result = await self.req(session, api)
            for repo in result.get('data'):
                repo_id = str(repo['id'])
                repo_name = repo['name']
                self.repo[repo_name] = repo_id
                self.repo_table.add_row([repo_id, repo_name])

    # 获取一个知识库的文档列表
    async def get_docs(self, repo_id):
        api = "/repos/%s/docs" % repo_id
        async with aiohttp.ClientSession() as session:
            result = await self.req(session, api)
            docs = {}
            for doc in result.get('data'):
                title = doc['title']
                slug = doc['slug']
                docs[slug] = title
            return docs

    # 获取正文 Markdown 源代码
    async def get_body(self, repo_id, slug):
        api = "/repos/%s/docs/%s" % (repo_id, slug)
        async with aiohttp.ClientSession() as session:
            result = await self.req(session, api)
            body = result['data']['body']
            body = re.sub("<a name=\".*\"></a>","", body)  # 正则去除语雀导出的<a>标签
            body = re.sub(r'\<br \/\>!\[image.png\]',"\n![image.png]",body) # 正则去除语雀图像前的<br \>标签,并换行
            body = re.sub(r'\)\<br \/\>', ")\n", body) # 正则去除语雀图像后的<br \>标签,并换行
            return body

    # 选择知识库
    def selectRepo(self):
        choices = [{"name": repo_name} for repo_name, _ in self.repo.items()]
        choices.insert(0, Separator('=== 知识库列表 ==='))
        questions = [
            {
                'type': 'checkbox',
                'qmark': '>>>',
                'message': '选择知识库',
                'name': 'repo',
                'choices': choices
            }
        ]
        repo_name_list = prompt(questions, style=custom_style_2)
        return repo_name_list["repo"]

    # 创建文件夹
    def mkDir(self, dir):
        isExists = os.path.exists(dir)
        if not isExists:
            os.makedirs(dir)

    # 获取文章并执行保存
    async def download_md(self, repo_id, slug, repo_name, title):
        """
        :param repo_id: 知识库id
        :param slug: 文章id
        :param repo_name: 知识库名称
        :param title: 文章名称
        :return: none
        """
        body = await self.get_body(repo_id, slug)
        new_body, image_list = await self.to_local_image_src(body)

        if image_list:
            # 图片保存位置: .yuque/<repo_name>/assets/<filename>
            save_dir = os.path.join(self.export_dir, repo_name, "assets")
            self.mkDir(save_dir)
            async with aiohttp.ClientSession() as session:
                await asyncio.gather(
                    *(self.download_image(session, image_info, save_dir) for image_info in image_list)
                )

        self.save(repo_name, title, new_body)

        print("📑 %s 导出成功！" % color(title, fore='green', style='bright'))

    # 将md里的图片地址替换成本地的图片地址
    async def to_local_image_src(self, body):
        body = re.sub(r'\<br \/\>!\[image.png\]',"\n![image.png]",body) # 正则去除语雀图像前的<br \>标签,并换行
        body = re.sub(r'\)\<br \/\>', ")\n", body) # 正则去除语雀图像后的<br \>标签,并换行
        
        pattern = r"!\[(?P<img_name>.*?)\]" \
                  r"\((?P<img_src>https:\/\/cdn\.nlark\.com\/yuque.*\/(?P<slug>\d+)\/(?P<filename>.*?\.[a-zA-z]+)).*\)"
        repl = r"![\g<img_name>](./assets/\g<filename>)"
        images = [_.groupdict() for _ in re.finditer(pattern, body)]
        new_body = re.sub(pattern, repl, body)
        return new_body, images

    # 下载图片
    async def download_image(self, session, image_info: dict, save_dir: str):
        img_src = image_info['img_src']
        filename = image_info["filename"]

        async with session.get(img_src) as resp:
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(await resp.read())

    # 保存文章
    def save(self, repo_name, title, body):
        # 将不能作为文件名的字符进行编码
        def check_safe_path(path: str):
            for char in r'/\<>?:"|*':
                path = path.replace(char, parse.quote_plus(char))
            return path

        repo_name = check_safe_path(repo_name)
        title = check_safe_path(title)
        save_path = "./yuque/%s/%s.md" % (repo_name, title)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(body)

    async def run(self):
        self.print_logo()
        await self.getRepo()
        repo_name_list = self.selectRepo()
        
        self.mkDir(self.export_dir)  # 创建用于存储知识库文章的文件夹

        # 遍历所选知识库
        for repo_name in repo_name_list:
            dir_path = self.export_dir + "/" + repo_name.replace("/", "%2F")
            dir_path.replace("//", "/")
            self.mkDir(dir_path)

            repo_id = self.repo[repo_name]
            docs = await self.get_docs(repo_id)

            await asyncio.gather(
                *(self.download_md(repo_id, slug, repo_name, title) for slug, title in docs.items())
            )

        print("\n" + color('🎉 导出完成！', fore='green', style='bright'))
        print("已导出到：" + color(os.path.realpath(self.export_dir), fore='green', style='bright'))


if __name__ == '__main__':
    export = ExportMD()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(export.run())
