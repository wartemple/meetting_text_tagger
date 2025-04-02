import re

def cut_sentences(text):
    # 使用正则表达式进行句子切分
    # 处理单字符断句符和省略号
    text = re.sub(r'([。！？])([^”’])', r"\1\n\2", text)  # 单字符断句符
    text = re.sub(r'(\.{6})([^”’])', r"\1\n\2", text)  # 英文省略号
    text = re.sub(r'(\…{2})([^”’])', r"\1\n\2", text)  # 中文省略号
    text = re.sub(r'([。！？][”’])([^，。！？\?])', r'\1\n\2', text)  # 双引号处理
    return text.splitlines()

# 示例文本
text = "今天天气很好！你想去哪里？我打算去公园……真是个好主意。"
sentences = cut_sentences(text)
for sentence in sentences:
    print(sentence.strip())
