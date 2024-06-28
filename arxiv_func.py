import arxiv
from datetime import datetime, timedelta, date
import os
from pathlib import Path
from openai import OpenAI
import time
import pandas as pd

# 发送邮件
import smtplib
import email.utils
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

import json


def arxiv_search(query, max_search_results): 
    """生成arxiv.Client和arxiv.Search"""
    client_arxiv = arxiv.Client()

    search = arxiv.Search(
        query = query,
        max_results = max_search_results,
        sort_by = arxiv.SortCriterion.LastUpdatedDate
    )

    return(client_arxiv, search)

def qwen_read(client, folder, file_name, arxiv_paper):
    """使用Qwen阅读文章"""
    try:
        print("开始阅读文章：", arxiv_paper.title)
        file_object = client.files.create(file=Path(folder) / file_name, purpose="file-extract")
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
        
        summary = completion.choices[0].message.model_dump()['content']   
        summary = "**Title**: {0}\n\n".format(arxiv_paper.title) + \
                    "**Authors**: {0}\n\n".format(", ".join(str(author) for author in arxiv_paper.authors)) + \
                        "**Categories**: {0}\n\n".format(", ".join(arxiv_paper.categories)) + summary
                
        with open(Path(folder) / "{0}.md".format(file_object.filename), "w", encoding="utf-8") as f:
            f.write(summary)
        return(True)
    except Exception as error:
        print("文档阅读失败。")
        print(error)
        return(False)
    
def download_paper(arxiv_result, new_folder):
    """下载指定arxiv文章"""
    arxiv_id = arxiv_result.entry_id.split('/abs/')[-1]
    print("Downloading", arxiv_id + "...")
    # 如果pdf文件已经存在则跳过
    if os.path.exists(Path(new_folder) / (arxiv_id + ".pdf")):
        print(arxiv_id, arxiv_result.updated.date(), "exists.")
    else:
        for retry in range(3):
            try: 
                arxiv_result.download_pdf(dirpath = new_folder, filename = arxiv_id + ".pdf")
                print(arxiv_id, arxiv_result.updated.date(), "downloaded.")
                break
            except:
                print("Download failed. Retrying...")
                time.sleep(5)
                continue

def read_day(client_arxiv, search, search_date, default_folder, qwen_client):
    """阅读当日的所有文章"""
    print("Reading papers on", search_date.strftime('%Y-%m-%d') + "...")
    new_folder = default_folder + "/" + search_date.strftime('%Y-%m-%d')
    os.makedirs(new_folder, exist_ok=True)

    for result in client_arxiv.results(search):
        if(result.updated.date() == search_date):
            arxiv_id = result.entry_id.split('/abs/')[-1]
            # 下载pdf文件
            download_paper(result, new_folder)
            # 如果md文件已经存在则跳过
            if os.path.exists(Path(new_folder) / (arxiv_id + ".pdf.md")):
                print(arxiv_id, "have been read.")
                continue
            # 如果阅读失败则存入error_papers.md
            elif not qwen_read(client=qwen_client, folder=new_folder, file_name=arxiv_id + ".pdf", arxiv_paper=result):
                with open(Path(new_folder) / "error_papers.md", "a") as error_papers:
                    error_papers.write("**Title**:" + result.title + "\n")
                    error_papers.write("**Summary**:" + result.summary + "\n\n")
        elif(result.updated.date() < search_date):
            print("No more papers to read.")
            break
        
    # 将所有输出整合到一个md文档中
    print("Integrating all outputs...")
    output_file = Path(new_folder) / "{0}.md".format(search_date.strftime('%Y-%m-%d'))
    with open(output_file, "w", encoding="utf-8") as f:
        for filename in os.listdir(new_folder):
            if filename.endswith(".md") and filename != "error_papers.md" and filename != "summary_filter" + search_date.strftime('%Y-%m-%d') + ".md":
                with open(default_folder + "/{0}/{1}".format(search_date.strftime('%Y-%m-%d'),filename), "r", encoding="utf-8") as f1:
                    f.write(f1.read())
                    f.write("\n\n")
    
    return(True)

def search_date_range(client_arxiv, search, default_folder, latest_date):
    """检索阅读最新更新的未阅读的文章，默认更新到最新文章更新时间之前的一天"""
    # 检索最新文章更新时间
    first_result = next(client_arxiv.results(search))
    recent_time = first_result.updated
    end_time = recent_time - timedelta(days=1)
    mail_txt = open(Path(default_folder) / "mail.txt", "w")
    if latest_date == end_time.date():
        # 如果没有需要阅读的文章，在mail.txt记录
        mail_txt.write("今日无文章更新。")
        mail_txt.close()
        return(None)
    elif latest_date < end_time.date():
        # 如果有更新阅读的文章，在mail.txt中记录阅读的时间区间
        if latest_date == end_time.date() - timedelta(days=1):
            mail_txt.write("今日更新" + end_time.date().strftime('%Y-%m-%d') + "的文章。")
        if latest_date < end_time.date() - timedelta(days=1):
            mail_txt.write("今日更新" + (latest_date + timedelta(days=1)).strftime('%Y-%m-%d') + "至" + \
                        end_time.date().strftime('%Y-%m-%d') + "的文章。")
        mail_txt.close()
        return(pd.date_range(latest_date + timedelta(days=1), end_time.date()).date)
    

def read_new(client_arxiv, search, default_folder, qwen_client, date_range):
    """阅读date_range时间范围内的文章"""
    for search_date in date_range:
        read_day(client_arxiv, search, search_date, default_folder, qwen_client)
    return(True)

def summary_and_filter(qwen_client, search_date, default_folder):
    """总结筛选当日感兴趣文章"""
    print("Filtering interesting papers...")
    try: 
        new_folder = default_folder + "/" + search_date.strftime('%Y-%m-%d')
        output_file = Path(new_folder) / "{0}.md".format(search_date.strftime('%Y-%m-%d'))
        file_object = qwen_client.files.create(file=output_file, purpose="file-extract")
        completion = qwen_client.chat.completions.create(
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
                                            并按照以上5类分别它们的总结整理出来。使用markdown格式进行总结，\
                                                markdown格式中，不使用markdown#标题格式，仅使用加粗格式，在每个条目中，展示出文章标题和作者。'
                        }
                    ],
                    stream=False
                )
        summary = completion.choices[0].message.model_dump()['content']
        with open(Path(new_folder) / ("summary_filter" + search_date.strftime('%y-%m-%d') + ".md"), "w", encoding="utf-8") as f:
                f.write(summary)
    except Exception as error:
        print("Filtering failed.")
        print(error)
            
def send_email(sender, receivers, auth_code, 
               sender_name, receiver_name, default_folder, date_range):
    """发送邮件"""
    sender = sender  # 发送邮箱
    receivers = receivers  # 接收邮箱
    auth_code = auth_code  # 授权码

    message = MIMEMultipart()
    message['From'] = email.utils.formataddr((sender_name, sender))  # 发送者
    message['To'] = email.utils.formataddr((receiver_name, receivers[0]))  # 接收者
    # 发送邮件主题
    message['Subject'] = Header("每日Arxiv AI总结", 'utf-8')
    # 邮件正文
    with open(Path(default_folder) / "mail.txt", "r") as f:
        message.attach(MIMEText(f.read(), 'plain', 'utf-8'))

    # 附件
    if date_range is not None:
        for search_date in date_range:
            summary_filename = Path(default_folder) / search_date.strftime('%Y-%m-%d') / (search_date.strftime('%Y-%m-%d') + ".md")
            summary_file = MIMEApplication(open(summary_filename, 'rb').read())  
            summary_file["Content-Type"] = 'application/octet-stream'  
            summary_file.add_header('Content-Disposition', 'attachment', filename=search_date.strftime('%Y-%m-%d') + ".md")
            message.attach(summary_file)
            if os.path.exists(Path(default_folder) / search_date.strftime('%Y-%m-%d') / ("summary_filter" + search_date.strftime('%Y-%m-%d') + ".md")):
                filter_filename = Path(default_folder) / search_date.strftime('%Y-%m-%d') / ("summary_filter" + search_date.strftime('%Y-%m-%d') + ".md")
                filter_file = MIMEApplication(open(filter_filename, 'rb').read())  
                filter_file["Content-Type"] = 'application/octet-stream'  
                filter_file.add_header('Content-Disposition', 'attachment', filename="summary_filter" + search_date.strftime('%Y-%m-%d') + ".md")
                message.attach(filter_file)
            if os.path.exists(Path(default_folder) / search_date.strftime('%Y-%m-%d') / "error_papers.md"):
                error_filename = Path(default_folder) / search_date.strftime('%Y-%m-%d') / "error_papers.md"
                error_file = MIMEApplication(open(error_filename, 'rb').read())  
                error_file["Content-Type"] = 'application/octet-stream'  
                error_file.add_header('Content-Disposition', 'attachment', filename="error_papers.md")
                message.attach(error_file)

    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(sender, auth_code)
        server.sendmail(sender, receivers, message.as_string())
        server.set_debuglevel(True)
        print("邮件发送成功")
        server.close()
        return(True)
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
        print(smtplib.SMTPException)
        return(False)

def read_arxiv(qwen_long_api, default_folder, latest_date, query, max_search_results,
               sender, receivers, auth_code, sender_name, receiver_name):
    """阅读arxiv文章"""
    client_arxiv, search = arxiv_search(query, max_search_results)
    # 登录Qwen Long模型
    qwen_client = OpenAI(
        api_key=qwen_long_api,  
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 填写DashScope服务endpoint
    )
    # 删除已上传的文件
    print("Deleting all updated files...")
    for file in qwen_client.files.list():
        qwen_client.files.delete(file_id=file.id)
    # 获取更新时间
    print("Get the latest update time...")
    date_range = search_date_range(client_arxiv, search, default_folder, latest_date)
    # 阅读最新更新的文章
    print("Reading papers...")
    if date_range is not None:
        read_new(client_arxiv, search, default_folder, qwen_client, date_range)
        # 生成总结筛选文章
        for search_date in date_range:
            summary_and_filter(qwen_client, search_date, default_folder)
    # 发送邮件
    print("Sending email...")
    send_email(sender=sender, receivers=receivers, auth_code=auth_code, sender_name=sender_name, receiver_name=receiver_name, 
               default_folder=default_folder, date_range=date_range)
    # 更新最新阅读时间
    print("Update the latest reading time...")
    if date_range is not None:
        with open(Path(default_folder) / "parameters.json", "r") as f:
            parameters = json.loads(f.read())
        parameters["latest_date"] = date_range[-1].strftime('%Y-%m-%d')
        with open(Path(default_folder) / "parameters.json", "w") as f:
            f.write(json.dumps(parameters))
    return(True)

# 默认参数保存在parameters.json文件中
# parameters = json.load(open("/root/ai_read_papers/parameters.json", "r"))
parameters = json.load(open("D:/Statistics/AI/parameters.json", "r"))
# qwen-long api
qwen_long_api = parameters["qwen_long_api"]
# 默认文件夹，每日文章将保存在默认文件夹/日期文件夹中，例如 ./默认文件夹/20240625
default_folder = parameters["default_folder"]
# 最新阅读时间，默认为最新arxiv检索时间-1天，如最新检索到20240625的文章，则阅读20240624前的文章
# 一般情况下只会新增一天，但是周末arxiv不更新，所以可能会有多天的文章需要阅读
latest_date = datetime.strptime(parameters["latest_date"], '%Y-%m-%d').date()
# 搜索arxiv的query，例如"cat:stat.ME OR cat:stat.AP OR cat:stat.CO OR cat:stat.ML OR cat:stat.TH OR cat:stat.OT"
query = parameters["query"]
# arxiv搜索结果数量，例如200
max_search_results = parameters["max_search_results"]
# 发送邮件的邮箱和接收邮件的邮箱
sender = parameters["sender"]
receivers = parameters["receivers"]
# 发送邮件的授权码
auth_code = parameters["auth_code"]
# 发送邮件的名称和接收邮件的名称
sender_name = parameters["sender_name"]
receiver_name = parameters["receiver_name"]

# 运行程序下载arxiv文章上传到Qwen Long模型阅读，并发送邮件
read_arxiv(qwen_long_api, default_folder, latest_date, query, max_search_results,
              sender, receivers, auth_code, sender_name, receiver_name)



    