import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langchain_tavily import TavilySearch
from tools.query_db import query_vector_db  # 你的自定义模块

load_dotenv()

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# 定义工具（复用你现有的函数）
from langchain_core.tools import tool

@tool
def search_with_db(query: str, collection_name: str) -> str:
    """进行数据库查询"""
    docs = query_vector_db(query, collection_name)
    return "\n".join([f"{doc.page_content}\n" for doc in docs])

# 包装 TavilySearch 为一个可调用函数
tavily_tool = TavilySearch()

# 将工具映射为函数名 -> 可调用对象
TOOL_MAP = {
    "search_with_db": search_with_db.func,
    "tavily_search": tavily_tool.run,
}

# 定义 tools 的 OpenAI 格式（供 API 使用）
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_with_db",
            "description": "在个人知识库数据库中查询信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "查询问题"},
                    "collection_name": {"type": "string", "description": "集合名称"}
                },
                "required": ["query", "collection_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "使用网络搜索引擎查找最新信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        }
    }
]

def run_conversation(user_query: str):
    """执行一次完整的问答（可能包含多轮工具调用）"""
    messages = [{"role": "user", "content": user_query}]
    turn = 1

    while True:
        # 调用 API，启用 thinking 模式
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            tools=tools,
            extra_body={"thinking": {"type": "enabled"}},
            stream=False  # 为简化示例，不使用流式
        )

        # 获取助手消息
        assistant_message = response.choices[0].message
        reasoning_content = assistant_message.reasoning_content
        content = assistant_message.content
        tool_calls = assistant_message.tool_calls
        # 打印调试信息（可选）
        print(f"\n--- Turn {turn} ---")
        if reasoning_content:
            print(f"推理过程：{reasoning_content}")
        if content:
            print(f"最终答案：{content}")
        if tool_calls:
            print(f"需要调用的工具：{tool_calls}")

        # 将完整的助手消息添加到历史中（包含 reasoning_content）
        messages.append(assistant_message)

        # 如果没有工具调用，说明已得到最终答案，结束循环
        if not tool_calls:
            break

        # 处理所有工具调用
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # 调用对应的本地函数
            if function_name in TOOL_MAP:
                result = TOOL_MAP[function_name](**function_args)
            else:
                result = f"错误：未知工具 {function_name}"

            # 将工具结果添加到消息历史
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        turn += 1

    # 返回最终答案（最后一条助手消息的 content）
    return assistant_message.content

# 使用示例
if __name__ == "__main__":
    query = "帮我查一下关于机器学习的知识，如果数据库没有，就搜索网络"
    final_answer = run_conversation(query)
    print("\n最终回答：", final_answer)