import json
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from core.config import DYNAMO_CHAT
from models.chat import ChatState


class DynamoChat:
    def __init__(self) -> None:
        dynamodb = boto3.resource(
            "dynamodb",
            region_name="ap-northeast-1",
        )
        self.table = dynamodb.Table(DYNAMO_CHAT)

    def insert_chat(
        self,
        state: ChatState,
        chat_id: str,
        user_id: str,
    ) -> None:
        self.table.put_item(
            Item={
                "chat_id": chat_id,
                "timestamp": int(time.time()),
                "user_id": user_id,
                "state": json.loads(state.json(ensure_ascii=False)),
            }
        )

    def create_user_id(self):
        while True:
            user_id = str(uuid.uuid4())
            resp = self.table.query(
                IndexName="UserIdIndex",
                KeyConditionExpression=Key("user_id").eq(user_id),
            )
            if resp["Count"] == 0:
                break

        return user_id

    def create_chat_id(self) -> str:
        while True:
            chat_id = str(uuid.uuid4())
            resp = self.table.query(KeyConditionExpression=Key("chat_id").eq(chat_id))
            if resp["Count"] == 0:
                break

        return chat_id

    def get_state(self, chat_id: str):
        res = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("chat_id").eq(chat_id),
            Limit=1,
            ScanIndexForward=False,  # Get the latest timestamp first.
        )
        return res["Items"][0]["state"]
