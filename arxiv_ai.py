import arxiv
from datetime import datetime, timedelta
import os
from pathlib import Path
from openai import OpenAI
import time

# 参数设定
max_search_results = 100 # 最多搜索的论文数,不影响下载的论文数，会自动选取最新一天的论文下载
# 这里输入你的API_KEY，在https://bailian.console.aliyun.com/ 申请
# qwen_long_api = "YOUR API HERE" 
# 或者读取qwen_api.txt文件中的API_KEY
with open("qwen_api.txt", "r") as f:
    qwen_long_api = f.read().strip()
default_folder = "D:/Statistics/AI/" # 默认的文件夹路径

# 搜索arxiv论文，返回最新max_search_results篇的统计学论文

client_arxiv = arxiv.Client()

search = arxiv.Search(
  # query = "cat:stat.ME OR cat:stat.AP OR cat:stat.CO OR cat:stat.ML OR cat:stat.TH OR cat:stat.OT",
  query = "cat:stat.ME OR cat:stat.ML OR cat:stat.TH",
  max_results = max_search_results,
  sort_by = arxiv.SortCriterion.LastUpdatedDate
)

first_result = next(client_arxiv.results(search))
recent_time = first_result.updated
print("Search papers from", recent_time.date())

# 登录Qwen Long模型
client = OpenAI(
    api_key=qwen_long_api,  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务endpoint
)

# 删除已上传的文件
print("Deleting all updated files...")
for file in client.files.list():
    client.files.delete(file_id=file.id)

# 下载当天论文并使用qwen-long阅读

new_folder = default_folder + recent_time.date().strftime('%Y-%m-%d')
os.makedirs(new_folder, exist_ok=True)
paper_count = 0
error_reading_count = 0
error_papers = []
for result in client_arxiv.results(search):
    # 如果时间不是当天则停止
    if result.updated.date() != recent_time.date():
        break
    paper_count += 1
    arxiv_id = result.entry_id.split('/abs/')[-1]
    # 如果pdf文件已经存在则跳过
    if os.path.exists(Path(new_folder) / (arxiv_id + ".pdf")):
        print(arxiv_id, result.updated.date(), "exists.")
    else:
        result.download_pdf(dirpath = new_folder, filename = arxiv_id + ".pdf")
        print(arxiv_id, result.updated.date(), "downloaded.")
    # Qwen Long模型阅读
    # 如果md文件已经存在则跳过
    if os.path.exists(Path(new_folder) / (arxiv_id + ".pdf.md")):
        print(arxiv_id, "have been read.")
        continue
    try:
        file_object = client.files.create(file=Path(new_folder) / (arxiv_id + ".pdf"), purpose="file-extract")
        completion = client.chat.completions.create(
                model="qwen-long",
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful scientific assistant. \
                            You are willing to provide accurate and helpful answers to users.'
                    },
                    {
                        'role': 'system',
                        'content': f'fileid://{file_object.id}'
                    },
                    {
                        'role': 'user',
                        'content': '请为我概括这篇统计学学术论文的核心要点，包括但不限于研究目的、具体方法、关键结果、核心贡献以及未来展望等方面。\
                            在总结过程中，请确保提炼出论文中最重要的核心内容，首先使用一句话总结文章的内容，\
                                然后再进行详细的总结。请使用markdown格式进行总结，\
                                    markdown格式中，不使用markdown#标题格式，仅使用加粗格式。'
                    }
                ],
                stream=False
            )
        
        print("Reading " + result.title + "...")
        summary = completion.choices[0].message.model_dump()['content']
        
        summary = "**Title**: {0}\n\n".format(result.title) + \
            "**Authors**: {0}\n\n".format(", ".join(str(author) for author in result.authors)) + \
                "**Categories**: {0}\n\n".format(", ".join(result.categories)) + summary
        
        with open(Path(new_folder) / "{0}.md".format(file_object.filename), "w", encoding="utf-8") as f:
            f.write(summary)
        # Sleep 5s to avoid exceeding the rate limit
        time.sleep(5)
    except:
        # 如果出现错误则跳过
        print("Error reading", result.title)
        error_reading_count += 1
        error_papers.append(result)
        continue
print("There are {0} papers".format(paper_count))
print("There are {0} papers failed to read".format(error_reading_count))

# 将所有输出整合到一个md文档中
print("Integrating all outputs...")
output_file = Path(new_folder) / "{0}.md".format(recent_time.date().strftime('%Y-%m-%d'))
with open(output_file, "w", encoding="utf-8") as f:
    for filename in os.listdir(new_folder):
        if filename.endswith(".md"):
            with open(default_folder + "{0}/{1}".format(recent_time.date().strftime('%Y-%m-%d'),filename), "r", encoding="utf-8") as f1:
                f.write(f1.read())
                f.write("\n\n")

with open(Path(new_folder) / "error_reading.md", "w", encoding="utf-8") as f:
    for paper in error_papers:
        f.write("**Title**:" + paper.title + "\n")
        f.write("**Summary**" + paper.summary + "\n\n")
                
# 总结筛选出当天论文中感兴趣的文章
print("Filtering interesting papers...")
file_object = client.files.create(file=output_file, purpose="file-extract")
completion = client.chat.completions.create(
            model="qwen-long",
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful scientific assistant. \
                        You are willing to provide accurate and helpful answers to users.'
                },
                {
                    'role': 'system',
                    'content': f'fileid://{file_object.id}'
                },
                {
                    'role': 'user',
                    'content': '这是今天arxiv最新统计学文章的总结，\
                        我对统计推断(Statistical Inference)、双机器学习(Double Machine Learning)、\
                            因果推断(Causal Inference)、半监督学习(Semi-Supervised Learning)、\
                                和传统统计学等主题比较感兴趣，请帮我筛选出其中所有与这些主题相关的文章，\
                                    并将它们的总结整理出来。'
                }
            ],
            stream=False
        )
summary = completion.choices[0].message.model_dump()['content']
with open(Path(new_folder) / "summary_filter.md", "w", encoding="utf-8") as f:
        f.write(summary)