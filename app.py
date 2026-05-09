import chainlit as cl
from ai.agent import create_my_agent
from langchain_core.messages import AIMessageChunk, ToolMessage

@cl.on_chat_start
async def on_chat_start():
    build_agent = create_my_agent()
    agent = await build_agent()

    cl.user_session.set("agent", agent)

    welcome_message = """
    **歡迎使用樂園營運決策助手系統**
    我可以協助您：
    A.查詢即時天氣資訊
    B.根據天氣提供設施營運建議
    C.推播營運決策通知

    使用方式：
    1. 直接詢問天氣狀況 例如：「現在的天氣如何？」
    2. 詢問特定天氣的營運規則 例如：「雨天時哪些設施要關閉？」
    3. 請求綜合建議 例如：「根據目前天氣，給我營運建議」
    4. 推播LINE Notify通知
    """

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):

    agent = cl.user_session.get("agent")

    ui_msg = cl.Message(content="思考中...")
    await ui_msg.send()

    final_text = ""

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": message.content}]},
        stream_mode="messages",
    ):
        msg = chunk[0]
        if isinstance(msg, ToolMessage):
            tool_name = msg.name
            ui_msg.content = f"呼叫工具中：{tool_name}..."
            await ui_msg.update()
        elif isinstance(msg, AIMessageChunk):
            if msg.content:
                text = ""
                for block in msg.content:
                    if block["type"] == "text":
                        text += block["text"]
                if text:
                    if final_text == "":
                        ui_msg.content = "生成回應中...\n\n"

                    final_text += text
                    ui_msg.content = "回覆內容如下:\n\n" + final_text
                    await ui_msg.update()
                    
    ui_msg.content = final_text
    await ui_msg.update()
