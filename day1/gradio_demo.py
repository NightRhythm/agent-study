import gradio as gr

def reverse_text(text):
    return text[::-1]

demo = gr.Interface(
    fn=reverse_text,
    inputs="text",
    outputs="text"
)

if __name__ == "__main__":
    demo.launch()