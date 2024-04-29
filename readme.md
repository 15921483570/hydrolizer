# Hydrolizer
Easy to convert a problem to HydroOJ format.

常常会遇到大量题库无法转化到自己的 OJ 上，本工具可以将抽取好的信息自动组装成符合 HydroOJ 格式的题目并自动压缩，解决后半部分的转化工作。

## Usage

只需导入本包后，按照范例，将所需信息以字典形式传入 `Hydrolizer()` 即可。

如需将 `Hydrolizer.hpath` 目录内的所有题目文件夹打包，可以直接调用 `Hydrolizer.zipzip()`。打包好的文件可以直接上传 HydroOJ 使用。

至于源文件的信息抽取，很遗憾，因源文件种类多样，无法统一写解析，只能根据实际情况，自行另写一个解析器以完成前半部分工作，本工具仅能实现后半部分工作。

## Example

```python
import hydrolizer

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

```

## Notes

包内自带一个 test 用例，可以直接运行 `__init__.py` 文件查看使用效果。