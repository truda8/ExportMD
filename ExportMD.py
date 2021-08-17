# -*- coding: UTF-8 -*-
# -----------------------------------------
# createTime : 2021-08-17
# author     : Truda
# email      : truda8@pm.me
# description: 自动导出语雀知识库为Markdown格式
# -----------------------------------------

from asyncio.runners import run
from prettytable import PrettyTable
import os
import aiohttp
import asyncio
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
            return body
            # 去除第一行
            # body = body.split("\n")[1:]
            # return "\n".join(body)  

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

    # 保存文章
    def save(self, repo_name, title, body):
        repo_name = repo_name.replace("/", "%2F")
        title = title.replace("/", "%2F")
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

            # 获取知识库所有文章内容
            for slug, title in docs.items():
                body = await self.get_body(repo_id, slug)
                self.save(repo_name, title, body)
                print("📑 %s 导出成功！" % color(title, fore='green', style='bright'))
        print("\n" + color('🎉 导出完成！', fore='green', style='bright'))
        print("已导出到：" + color(os.path.realpath(self.export_dir), fore='green', style='bright'))


if __name__ == '__main__':
    export = ExportMD()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(export.run())
