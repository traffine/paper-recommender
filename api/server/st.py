import random

import streamlit as st
from core.character import INIT_WORDS
from models.chat import ChatState, Message, Role
from services.logics.recommender import PaperChatRecommender
from utils.dynamodb import DynamoChat

st.title("Paper Recommender")

dynamo_chat = DynamoChat()

if "user_id" not in st.session_state:
    user_id = dynamo_chat.create_user_id()
    st.session_state.user_id = user_id

if "chat_id" not in st.session_state:
    chat_id = dynamo_chat.create_chat_id()
    st.session_state.chat_id = chat_id

if "messages" not in st.session_state:
    init_word = random.choice(INIT_WORDS)
    state = ChatState(keywords=[], messages=[], excluded_ids=[])
    state.messages.append(Message(role=Role.ASSISTANT, content=init_word))

    dynamo_chat.insert_chat(chat_id=chat_id, user_id=user_id, state=state)

    st.session_state.messages = state.messages

# Show previous conversation
for message in st.session_state.messages:
    with st.chat_message(message.role.value):
        st.markdown(message.content)

# Start
if user_input := st.chat_input("ここから入力"):
    # User
    st.session_state.messages.append(Message(role=Role.USER, content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    state = ChatState(**dynamo_chat.get_state(chat_id=st.session_state.chat_id))
    print("state:", state)
    recommender = PaperChatRecommender(state=state)

    res = recommender.process(user_input=user_input)

    dynamo_chat.insert_chat(
        chat_id=st.session_state.chat_id,
        user_id=st.session_state.user_id,
        state=res["state"],
    )

    ai_outputs = (
        [res["ai_outputs"]] if type(res["ai_outputs"]) is str else res["ai_outputs"]
    )

    # Assistant
    with st.chat_message("assistant"):
        with st.spinner("回答を生成中です..."):
            for output in ai_outputs:
                st.markdown(output)
                st.markdown("\n")
    for output in ai_outputs:
        st.session_state.messages.append(Message(role=Role.ASSISTANT, content=output))
