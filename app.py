import chainlit as cl
from ai.agent import create_my_agent
from langchain_core.messages import AIMessageChunk, ToolMessage

@cl.on_chat_start
async def on_chat_start():
    agent = await create_my_agent()
    thread_config = {
        "configurable": {
            "thread_id": cl.user_session.get("id")
        }
    }

    cl.user_session.set("agent", agent)
    cl.user_session.set("thread_config", thread_config)


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
    thread_config = cl.user_session.get("thread_config")

    ui_msg = cl.Message(content="思考中...")
    await ui_msg.send()

    final_text = ""

    async for msg, _metadata in agent.astream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message.content
                }
            ]
        },
        config=thread_config,
        stream_mode="messages",
    ):
        if isinstance(msg, ToolMessage):
            tool_name = msg.name or "未知工具"
            ui_msg.content = f"呼叫工具中：{tool_name}..."
            await ui_msg.update()
        elif isinstance(msg, AIMessageChunk):
            text = msg.text
            if text:
                final_text += text
                ui_msg.content = "回覆內容如下:\n\n" + final_text
                await ui_msg.update()
                    
    ui_msg.content = final_text or "模型未產生文字回覆。"
    await ui_msg.update()
