from fastapi import HTTPException
from fastapi.routing import APIRouter
from loguru import logger
from models.ids import ChatId, UserId
from utils.dynamodb import DynamoChat

router = APIRouter()


@router.get("/create-user-id", response_model=UserId, name="User ID creation API")
async def create_user_id() -> UserId:
    """User ID creation API

    Create user ID

    Args:

    Returns:
        UserId: User ID
    """
    try:
        client = DynamoChat()
        user_id = client.create_user_id()
        return UserId(user_id=user_id)
    except TimeoutError as e:
        logger.error(e)
        raise HTTPException(status_code=408, detail=e) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=e) from e


@router.get("/create-chat-id", response_model=ChatId, name="Chat ID creation API")
async def create_chat_id():
    """Chat ID creation API

    Create chat ID

    Args:

    Returns:
        ChatId: Chat ID
    """
    try:
        client = DynamoChat()
        chat_id = client.create_chat_id()
        return ChatId(chat_id=chat_id)
    except TimeoutError as e:
        logger.error(e)
        raise HTTPException(status_code=408, detail=e) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=e) from e
