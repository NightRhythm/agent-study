from tools import get_weather, get_attraction
from client import OpenAICompatibleClient
import os
from dotenv import load_dotenv
import re

load_dotenv()
base_url = os.environ.get("BASE_URL")
api_key = os.environ.get("API_KEY")
model = os.environ.get("MODEL")


AGENT_SYSTEM_PROPMT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具：
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求：
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought：[你的思考过程和下一步计划]
Action：[你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示：
- 每次只输出一对Thought-Action
- Action必须在同一行，不换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action：Finish[最终答案] 格式结束

"""

available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}

llm = OpenAICompatibleClient(model, base_url, api_key)

user_prompt = "请为我推荐北京的旅游景点。"
prompt_history = [f"用户请求：{user_prompt}"]

print(f"用户输入：{user_prompt}\n" + "=" * 40)

for i in range(5):
    print(f"--- 循环{i+1} ---\n")

    full_prompt = "\n".join(prompt_history)

    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROPMT)
    # 模型可能会输出多余的 Thought-Action，需要截断
    match = re.search(
        r'(Thought\s*[:：].*?Action\s*[:：].*?)'
        r'(?=\n\s*(?:Thought|Action|Observation)\s*[:：]|\Z)',
        llm_output,
        re.DOTALL,
    )
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
        print(f"模型输出：\n{llm_output}\n")
        prompt_history.append(llm_output)

    # 解析并执行行动
    action_match = re.search(r"Action\s*[:：]\s*(.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "="*40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"任务完成，最终答案: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的工具 '{tool_name}'"

    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)