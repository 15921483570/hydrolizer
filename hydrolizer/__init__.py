import os
import requests
import shutil
import html2text
from urlextract import URLExtract
from textwrap import dedent
import zipfile


class Hydrolizer:
    hpath = 'hydro'
    DEFAULT_MEMORY = 256  # 限制内存，默认值为 256

    def __init__(self, fname, data_src='', headers=None, cookies=None, ignore=None,
                 pid='P1000', title='', difficulty=0, tags: list[str] = None, owner=2,
                 bg='', desc='', infmt='', outfmt='', trans='',
                 samples=None, hint='', tp='default', tm=1000, mem=DEFAULT_MEMORY):
        """根据文件名创建题目文件夹和数据文件夹"""
        self.fname, self.data_src, self.headers, self.cookies = fname, data_src, headers, cookies
        self.headers = headers if headers else {}
        self.cookies = cookies if cookies else {}
        self.fpath = os.path.join(Hydrolizer.hpath, fname)
        self.dpath = os.path.join(self.fpath, 'testdata')
        self.makedirs()
        self.add = False  # addtional file
        self.apath = ''  # 附件目录应按需创建，url_local 判断是否有图片/链接
        self.ignore = ignore if ignore else []  # 屏蔽网址关键词列表
        self.pid, self.title, self.difficulty, self.tags, self.owner = str(
            pid).strip(), title.strip(), difficulty, tags, owner
        h = html2text.HTML2Text()
        h.body_width = 0  # turn off text wrap, no random '\n'
        t = [h.handle(self.url_local(s)).strip() for s in (bg, desc, infmt, outfmt, trans, hint)]
        self.bg, self.desc, self.infmt, self.outfmt, self.trans, self.hint = t
        # print(t)
        self.samples = samples
        self.tp, self.tm, self.mem = tp, tm, mem

        self.check_key_params()
        self.hydrolize()

    def makedirs(self):
        if not os.path.exists(Hydrolizer.hpath):
            os.makedirs(Hydrolizer.hpath)
        if os.path.exists(self.fpath):
            shutil.rmtree(self.fpath)
        os.makedirs(self.fpath)
        os.makedirs(self.dpath)

    def check_key_params(self):
        if not self.data_src:
            print(f"⚠️警告！本题（{self.pid} {self.fname}）缺失 评测 数据！请注意检查！")
        if not self.title:
            raise ValueError(f"本题（{self.pid} {self.fname}）缺失 title 数据！请注意检查！")
        if not self.samples:
            raise ValueError(f"本题（{self.pid} {self.fname}）缺失 样例 数据！请注意检查！")
        if not self.desc:
            print(f"⚠️警告！本题（{self.pid} {self.fname}）无题目描述！请注意检查！")

    def url_local(self, s):

        extractor = URLExtract()
        urls = extractor.find_urls(s)
        if urls:
            if not self.add:  # 第一次发现 url
                self.add = True
                self.apath = os.path.join(self.fpath, 'additional_file')
                if not os.path.exists(self.apath):
                    os.makedirs(self.apath)
            for url in urls:
                if self.ignore:
                    for ignore in self.ignore:
                        if ignore in url:
                            continue
                if url.split('.')[-1] in ['jpg', 'jpeg', 'png', 'gif', 'zip', 'pdf']:
                    r = requests.get(url, headers=self.headers, cookies=self.cookies)
                    if r.status_code == 200:
                        iname = url.split('/')[-1]
                        ipath = os.path.join(self.apath, iname)
                        with open(ipath, 'wb') as f:
                            a = f.write(r.content)
                        new_url = f'file://{iname}'
                        s = s.replace(url, new_url)
                    else:
                        print(url, r.status_code, '⚠️警告！文件无法下载，请检查网址、headers/UA 和 cookies。')

        return s

    def problem_md(self):
        content = ""
        if self.bg:
            content += f"## 题目背景\n\n{self.bg}\n\n"
        if self.desc:
            content += f"## 题目描述\n\n{self.desc}\n\n"
        if self.infmt:
            content += f"## 输入格式\n\n{self.infmt}\n\n"
        if self.outfmt:
            content += f"## 输出格式\n\n{self.outfmt}\n\n"
        if self.trans:
            content += f"## 题目大意\n\n{self.trans}\n\n"

        for t, (i, o) in enumerate(self.samples, start=1):
            if not i.strip() and not o.strip():
                print(f"⚠️警告！本题（{self.pid} {self.fname}）缺失第 {t} 组样例数据！请注意检查！")
            content += f"```input{t}\n{i}\n```\n\n"
            content += f"```output{t}\n{o}\n```\n\n"

        if self.hint:
            content += f"## 提示\n\n{self.hint}\n\n"

        path = os.path.join(self.fpath, 'problem.md')
        with open(path, 'w') as f:
            f.write(content)

        return content

    def problem_yaml(self):
        content = dedent(f"""
        pid: '{self.pid}'
        owner: {self.owner}
        title: '{self.title}'
        """).strip('\n')
        content += f"\ntag: {self.tags}" if self.tags else ""
        content += f"\ndifficulty: {self.difficulty}\n" if self.difficulty else ""

        name = os.path.join(self.fpath, 'problem.yaml')
        with open(name, 'w') as f:
            f.write(content)
        return content

    def conf_yaml(self):
        if self.tp == 'default' and self.tm == 1000 and self.mem == Hydrolizer.DEFAULT_MEMORY:
            return
        content = dedent(f"""
        type: {self.tp}
        time: {self.tm}ms
        memory: {self.mem}m
        """).strip('\n')
        name = os.path.join(self.dpath, 'config.yaml')
        with open(name, 'w') as f:
            f.write(content)
        return content

    def hydrolize(self):
        self.problem_md()
        if self.data_src:
            self.copy_allfiles(self.data_src, self.dpath)
        self.problem_yaml()
        self.conf_yaml()
        print(self.fname, "生成完毕！")

    @staticmethod
    def copy_allfiles(src, dest):
        # src:原文件夹；dest:目标文件夹
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest)
            else:
                print("Skipping " + full_file_name, 'reason: not a file')

    @staticmethod
    def zipzip() -> None:
        prefix = Hydrolizer.hpath
        zname = os.path.join(prefix, "000.zip")
        with zipfile.ZipFile(zname, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            dirs = [i for i in os.listdir(prefix) if os.path.isdir(os.path.join(prefix, i))]
            for di in dirs:
                dd = os.path.join(prefix, di)
                z.write(dd, arcname=(n := di))
                print('zip_dirs:', n)
                for root, dirs, files in os.walk(dd):
                    for fn in files:
                        if fn == '.DS_Store' or fn.endswith('.zip'):  # 数据压缩包不太可能是有效数据
                            continue
                        z.write(
                            fp := os.path.join(root, fn),
                            arcname=(nn := os.path.relpath(fp, prefix)),
                        )
                    # print('fp_dirs:', nn)


if __name__ == "__main__":
    fname = "testttt"

    pid = 1
    data_src = os.path.join('test', 'data')

    d = {
        # 基本属性
        "fname": fname,  # 必填
        "data_src": data_src,  # 评测数据源文件夹路径，默认值为''，如无数据会报警告

        # 下载外部文件所需信息
        "headers": {},  # 默认值为 ''，如无数据可删除此行
        "cookies": {},  # 默认值为 {}，如无数据可删除此行
        "ignore": [],  # 屏蔽网址关键词列表, 格式为['屏蔽词1', '屏蔽词2', ...]，默认值为 []，如无数据可删除此行

        # problem.md, 文字部分会自动从 html 格式转为 Markdown
        "bg": "背景",  # 默认值为 ''，如无数据可删除此行
        "desc": "题目描述 ![](https://abc.com/123.png)",  # 默认值为 ''，如无数据会报警告，如存在外部图片链接会自动下载并整理
        "infmt": "输入格式",  # 默认值为 ''，如无数据可删除此行
        "outfmt": "输出格式",  # 默认值为 ''，如无数据可删除此行
        "trans": "题目大意",  # 默认值为 ''，如无数据可删除此行
        "samples": [['1', '2'], ['2', '3']],  # 必填，格式为：[第1组数据[输入，输出], 第2组数据[输入，输出], ...]
        # 如无样例数据会报 ValueError， 如某次输入输出均为空会报警告
        "hint": "提示",  # 默认值为 ''，如无数据可删除此行

        # problem.yaml
        "pid": f"P{pid}",  # 数字或字符串，默认值为'P1000'
        "owner": 2,  # 默认值为 2，如无特别要求可删除此行
        "title": "买笔",  # 必填，如无数据会报 ValueError
        "tags": ['选择'],  # 默认值为 None，格式为['标签1','标签2', ...]，如无特别要求可删除此行
        "difficulty": 1,  # 默认值为 0，如无特别要求可删除此行

        # ./testdata/config.yaml
        "tp": 'default',  # 题目类型，默认值为 'default'，如无特别要求可删除此行
        "tm": 1000,  # 限制时间，默认值为 1000，如无特别要求可删除此行
        "mem": 256,  # 限制内存，默认值为 256，如无特别要求可删除此行
        # 以上三项若全部为默认值，则不会生成 config.yaml 文件，评测时 oj 会自动处理
    }
    Hydrolizer.DEFAULT_MEMORY = 256  # 可根据题目实际情况调整默认限制内存，减少生成大量无效 config.yaml
    Hydrolizer(**d)  #
    Hydrolizer.zipzip()  # 打包 Hydrolizer.hpath 目录内的所有文件夹到 Hydrolizer.hpath/000.zip
