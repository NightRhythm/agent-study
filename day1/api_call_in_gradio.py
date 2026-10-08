import gradio as gr
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get('API_KEY'),
    base_url=os.environ.get('BASE_URL'))

model=os.environ.get('MODEL', 'deepseek-v4.1-flash')

def get_completion(text):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": text},
        ],
        stream=False,
        reasoning_effort="low",
    )

    return response.choices[0].message.content


demo = gr.Interface(
    fn=get_completion,
    inputs="text",
    outputs="text"
)

if __name__ == "__main__":
    demo.launch()