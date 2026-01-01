rag agent 返回source 内容的方式有两种

方案1：

a. agent 自己调用retrieval_service 去获得top k knowledge base chunk内容
b. agent 把k个chunk内容 全部发给llm去回答
c. agent 把llm的回答 加上chunk内容（by a step）组装一起返回给用户   


方案2：
a. 基于retrieval_service 构建一个tool ，创建一个tool calling agent

b. tool calling agent 调用工具获取top k knowledge base chunk内容, 并利用llm 回答问题， 最终把LLM的回答和chunk内容一并发给RAG AGENT
C. RAG AGENT 把LLM的回答和chunk内容一并发给用户


问题：
1. 当前代码使用哪个方案把chunk内容发给用户的？
2. 哪个方案是best practice？


但是方案2 ，chuck的内容要依赖llm输出， 会不会影响chunks内容的准确性？   