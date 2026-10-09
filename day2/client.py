from email import message

import openai

class OpenAICompatibleClient:
    """一个用于调用任何兼容OpenAI接口的LLM服务的客户端"""
    def __init__(self, model: str, base_url: str, api_key: str):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str):
        print("正在调用大语言模型...")
        try:
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )

            answer = response.choices[0].message.content
            print("模型响应成功")
            return answer

        except Exception as e:
            print(f"大模型调用时发生错误：{e}")
            return "错误：调用模型服务时出错。"