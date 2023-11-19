import gradio as gr
import os
import time
import pandas as pd
import numpy as np
from outlaw import Outlaw

outlaw = Outlaw()


def add_file(history, file):
    history = history + [((file.name, file.name.split(".")[-1]), None)]
    return history


def add_text(history, text):
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


def find_file(history):
    for h in history[::-1]:
        if type(h[0]) != str:
            if h[0][1] == "csv":
                return h


def find_desc(history):
    for h in history[::-1]:
        if type(h[0]) != str:
            if h[0][1] == "txt":
                return h


def check_is_run_outlaw(history):
    for h in history[::-1]:
        if type(h[1]) == str:
            if "This is your policy suggestion" in h[1]:
                return True


def bot(history):
    csv = find_file(history)
    desc = find_desc(history)
    response = ""
    if not check_is_run_outlaw(history):
        if csv is None:
            response += "Please upload a CSV file before starting talk to me\n"
        elif desc is None:
            response += "Please upload a description file before starting talk to me\n"
        else:
            outlaw.set_data(csv[0][0], desc[0][0])
            outlaw.start()
            response += "This is your policy suggestion\n"
            response += outlaw.response()
    else:
        response += outlaw.chat(history[-1][0])

    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.001)
        yield history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        bubble_full_width=False,
        height=700,
    )
    with gr.Row():
        upload_btn = gr.UploadButton(
            "📃 Upload",
            file_types=[".csv", ".txt"],
        )
        text = gr.Text(
            scale=6,
            show_label=False,
            placeholder="Enter text",
            container=False,
        )

    txt_msg = text.submit(add_text, [chatbot, text], [chatbot, text], queue=False).then(
        bot, chatbot, chatbot, api_name="bot_response"
    )

    txt_msg.then(lambda: gr.Textbox(interactive=True), None, [text], queue=False)

    file_msg = upload_btn.upload(
        add_file, [chatbot, upload_btn], [chatbot], queue=False
    ).then(bot, chatbot, chatbot)
demo.launch()
