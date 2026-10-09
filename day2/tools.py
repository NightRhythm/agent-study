from urllib import response

import requests
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

def get_weather(city: str) -> str :
    """通过调用 wttr.in API 查询真实天气信息"""

    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url)
        response.raise_for_status()  ## 检查状态码是否为 200
        data = response.json()

        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        # 格式化自然语言返回
        return f"{city} 当前天气：{weather_desc}, 气温 {temp_c} 摄氏度"

    except requests.exceptions.RequestException as e:
        return f"错误：查询天气时遇到问题 - {e}"
    except (KeyError, IndexError) as e:
        return f"错误：解析天气数据失败：{e}"

def get_attraction(city: str, weather: str) -> str:
    """根据城市和天气，使用 Tavily Search API 搜索并返回优化后的景点推荐"""

    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key:
        return f"错误：未配置 TAVILY_API_KEY"

    tavily = TavilyClient(api_key=tavily_api_key)

    query = f"'{city}' 在 '{weather}' 天气下最值得去的旅游景点和推荐理由"

    try:
        response = tavily.search(query=query, search_depth='basic', include_answer=True)
        if response.get("answer"):
            return response["answer"]

        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")

        if not formatted_results:
            return "抱歉，没有找到相应的旅游景点推荐"

        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误，执行 Tavily Search 时出现问题 - {e}"
