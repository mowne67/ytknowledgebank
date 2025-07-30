from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated, Literal

import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))



memory = MemorySaver()

def general_chat(state):
    system_message = SystemMessage(
        content=(
            "You are a YT Transcript and Subtitle Extraction Assistant. " \
            "I have given you a transcript of a YouTube video. " \
            "Your task is to summarize the content of the transcript in detail " \
            "You cannot have any opinion on the contents of the video" \
            "Treat it as a knowledge source, do not say speaker or the video" \
            "Provide your response in bullet points, with each point on a new line." \
                
        )
    )
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-pro",
temperature=0.4, max_output_tokens=7400)
    response = llm.invoke([system_message] + state['messages'])
    return {"messages": [response]}

class GraphState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to
propagate to, and modify in, each graph node.
    """
    messages: Annotated[list[AnyMessage], add_messages]



graph = StateGraph(GraphState)

graph.add_node('general_chat', general_chat)

graph.add_edge(START, "general_chat")

graph.add_edge("general_chat", END)
workflow = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

def get_output(user_input):
    final_output = workflow.invoke(
        {
            "messages": [HumanMessage(user_input)]
        },
        config={"configurable": {"thread_id": "1"}}
    )
    return final_output["messages"][-1].content


import re

def extract_text_from_srt(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove SRT index numbers and timestamps
    text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> .*?\n', '', content)
    # Remove any remaining timestamps
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> .*?\n', '', text)
    # Remove index numbers
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove empty lines
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def get_video_name_from_srt(srt_file):
    import os
    return os.path.splitext(os.path.basename(srt_file))[0]

def save_summary_to_markdown(summary, video_name, summary_dir='summary'):
    import os
    os.makedirs(summary_dir, exist_ok=True)
    md_output_path = os.path.join(summary_dir, f'{video_name}.md')
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary saved to {md_output_path}")
    return summary

# Example usage:
def summarize_srt_file(srt_file):
    clean_text = extract_text_from_srt(srt_file)
    video_name = get_video_name_from_srt(srt_file)
    summary = get_output(clean_text)
    return save_summary_to_markdown(summary, video_name)

# Uncomment and use as needed:
# srt_file = 'subtitles/your_file.srt'
# summarize_srt_file(srt_file)
