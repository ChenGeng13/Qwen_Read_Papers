# Qwen_Read_Papers
Download and read newest paper on arxiv by qwen-long.

# 功能
通过Arxiv api下载指定类别的文章，通过Qwen-long api批量阅读进行总结，最后再通过整理Qwen-long总结筛选出感兴趣的文章，自动将整理结果发送到自己的邮箱。

# 使用方法
+ 申请Qwen api
+ 申请邮箱授权码
+ 调整parameters_examples.json中的参数
+ 根据自己的兴趣调整arxiv_func.py中qwen_read函数和summary_and_filter中的prompt

# 例子
example文件夹中存储了运行阅读2024.06.26中文章总结和筛选的结果。

# 注意
+ 由于网络问题和Qwen的限制问题，部分文章可能阅读失败，失败文章的标题、作者和摘要会存储在error_reading.md中
+ 筛选功能实测效果并不好，可能需要更合适的prompt
