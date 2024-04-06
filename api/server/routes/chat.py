import random
import traceback

from core.character import INIT_WORDS
from fastapi import HTTPException
from fastapi.routing import APIRouter
from loguru import logger
from models.chat import Chat, ChatState, InitChat, Message, Role
from services.logics.recommender import PaperChatRecommender
from utils.dynamodb import DynamoChat

router = APIRouter()


@router.post("/init-chat", response_model=InitChat)
async def init_chat(user_id: str, chat_id: str):
    """Initial chat API

    Create initial AI text

    Args:
        user_id (str): User ID
        chat_id (str): Chat ID

    Returns:
        InitChat
    """
    try:
        init_word = random.choice(INIT_WORDS)
        state = ChatState(keywords=[], messages=[], excluded_ids=[])
        state.messages.append(Message(role=Role.ASSISTANT, content=init_word))

        client = DynamoChat()
        client.insert_chat(chat_id=chat_id, user_id=user_id, state=state)

        return InitChat(chat_id=chat_id, user_id=user_id, ai_outputs=[init_word])
    except TimeoutError as e:
        logger.error(e)
        raise HTTPException(status_code=408, detail=e) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=e) from e


@router.post("/chat", response_model=Chat)
async def chat(user_id: str, chat_id: str, user_input: str):
    """Chat API

    Create AI text based on user input

    Args:
        user_id (str): User ID
        chat_id (str): Chat ID
        user_input (str): user input

    Returns:
        Chat
    """
    try:
        client = DynamoChat()
        state = ChatState(**client.get_state(chat_id=chat_id))
        recommender = PaperChatRecommender(state=state)

        res = recommender.process(user_input=user_input)

        if (
            res["ai_outputs"] == ""
            or res["ai_outputs"] is None
            or res["ai_outputs"] == []
        ):
            raise HTTPException(status_code=400, detail="No response")

        client.insert_chat(chat_id=chat_id, user_id=user_id, state=res["state"])

        return Chat(
            chat_id=chat_id,
            user_id=user_id,
            ai_outputs=res["ai_outputs"],
            current_keywords=res["current_keywords"],
        )
    except TimeoutError as e:
        logger.error(e)
        raise HTTPException(status_code=408, detail=e) from e
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=e) from e
