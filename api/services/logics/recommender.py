import json
import unicodedata
from typing import Any, Dict, List, Optional

import MeCab
from core.character import RECOMMEND_WORD
from core.config import (
    CONV_HISTORY_COUNT,
    LOCAL,
    N_KW_EXTRACT,
    N_KW_STORE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from core.keyword import KEYWORDS, KEYWORDS_NORMED
from models.chat import ChatState, Message, Role
from openai import OpenAI
from services.prompts.keyword import keyword_prompt, negative_keyword_prompt
from services.prompts.summary import summarize_prompt
from services.prompts.talk import talk_prompt
from utils.pc import Pinecone


class PaperChatRecommender:
    def __init__(self, state: ChatState) -> None:
        """instance initialization

        Args:
            state (ChatState): chat state
        """
        self.state = state

    @staticmethod
    def oai_completion(
        messages: List[Message], system_prompt: str, user_input: Optional[str]
    ) -> Any:
        """OpenAI completions

        Args:
            messages (List[Message]): OpenAI chat history
            system_prompt (str): system prompt
            user_input (Optional[str]): user input

        Returns:
            str: OpenAI completions response
        """
        messages_ = [Message(role=Role.SYSTEM, content=system_prompt)] + messages

        if user_input:
            messages_ = messages_ + [Message(role=Role.USER, content=user_input)]

        messages_ = [
            json.loads(message.json(ensure_ascii=False)) for message in messages_
        ]

        client = OpenAI(api_key=OPENAI_API_KEY)

        res = (
            client.chat.completions.create(
                model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE, messages=messages_
            )
            .choices[0]
            .message.content
        )

        return res

    @staticmethod
    def filter_longest_prefix(strs: List[str]) -> list[str]:
        """Filtering longest prefix

        Keep the longest keyword and remove the others.
        For instance, if 'max' and 'maximum' are in list, 'max' will be removed.

        Args:
            strs (List[str]): keywords

        Returns:
            list[str]: keywords
        """
        strs_filtered: List[str] = []
        strs.sort(key=len, reverse=True)

        for current_str in strs:
            if not any(current_str in result_str for result_str in strs_filtered):
                strs_filtered.append(current_str)

        return strs_filtered

    def extract_keywords(self, user_input: str) -> list[str]:
        if LOCAL == "y":  # local
            m = MeCab.Tagger(
                '-Ochasen -r "venv/lib/python3.10/site-packages/ipadic/dicdir/mecabrc" -d "/opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd" -u "data/dictionary/user.dic"'
            )
        else:  # docker
            m = MeCab.Tagger(
                '-Ochasen -r "/usr/local/lib/python3.10/site-packages/ipadic/dicdir/mecabrc" -d "/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd" -u "data/dictionary/user.dic"'
            )

        user_input = unicodedata.normalize("NFKC", user_input.lower())

        nouns = [
            line.split("\t")[0]
            for line in m.parse(user_input).splitlines()
            if "固有名詞" in line.split()[-1] or "名詞-一般" in line.split()[-1]
        ]

        nouns = [unicodedata.normalize("NFKC", x.lower()) for x in nouns]

        keywords_matched_ = list(
            filter(
                lambda x: x in KEYWORDS_NORMED,
                nouns,
            )
        )

        keywords_matched = [
            x
            for x in KEYWORDS
            if unicodedata.normalize("NFKC", x.lower()) in keywords_matched_
        ]

        keywords_ai_str = self.oai_completion(
            [], keyword_prompt(user_input=user_input), None
        )
        keywords_ai_str = keywords_ai_str if type(keywords_ai_str) is str else ""
        keywords_ai = [keyword.strip() for keyword in keywords_ai_str.split(",")]
        keywords_ai = list(filter(lambda x: x in KEYWORDS, keywords_ai))

        if len(keywords_ai) > N_KW_EXTRACT:
            keywords_ai = keywords_ai[:N_KW_EXTRACT]

        unique_keywords = list(set(keywords_matched + keywords_ai))

        negative_keywords_str = self.oai_completion(
            messages=[],
            system_prompt=negative_keyword_prompt(
                user_input=user_input, keywords=unique_keywords
            ),
            user_input=None,
        )

        negative_keywords_str = (
            negative_keywords_str if type(negative_keywords_str) is str else ""
        )

        negative_keywords = [
            keyword.strip() for keyword in negative_keywords_str.split(",")
        ]
        negative_keywords = list(filter(lambda x: x != "", negative_keywords))

        keywords = list(filter(lambda x: x not in negative_keywords, unique_keywords))
        keywords = list(filter(None, keywords))
        keywords = self.filter_longest_prefix(keywords)

        return keywords

    def process(self, user_input: str) -> Dict:
        """Process

        Args:
            user_input (str): user input

        Returns:
            Dict: dict
        """
        current_keywords = []

        # keyword
        keywords = self.extract_keywords(user_input=user_input)
        self.state.keywords = list(set(self.state.keywords + keywords))

        if len(self.state.keywords) >= N_KW_STORE:
            # Pinecone search
            pinecone = Pinecone()
            query = pinecone.query(
                user_input=user_input,
                keywords=self.state.keywords,
                excluded_ids=self.state.excluded_ids,
            )
            query_matches = query["matches"]

            if len(query_matches):
                ai_output = [RECOMMEND_WORD] + [
                    f"タイトル：{q['metadata']['title']}\n\n"
                    + f"概要：{q['metadata']['abstract'][:50]}...\n\n"
                    + f"キーワード：{', '.join(q['metadata']['keywords'])}\n\n"
                    + f"DOI：{q['metadata']['doi']}"
                    for q in query_matches
                ]

                self.state.excluded_ids = self.state.excluded_ids + [
                    q["id"] for q in query_matches
                ]
                current_keywords = self.state.keywords
                self.state.keywords = []
            else:
                ai_output = self.oai_completion(
                    messages=self.state.messages,
                    system_prompt=talk_prompt(),
                    user_input=user_input,
                )
        else:
            ai_output = self.oai_completion(
                messages=self.state.messages,
                system_prompt=talk_prompt(),
                user_input=user_input,
            )

        # update state
        self.state.messages.append(Message(role=Role.USER, content=user_input))
        self.state.messages.append(
            Message(
                role=Role.ASSISTANT,
                content=(ai_output if type(ai_output) is str else "\n".join(ai_output)),
            )
        )

        if len(self.state.messages) > CONV_HISTORY_COUNT:
            all_chats = "- " + "\n - ".join(
                [item["content"] for item in self.state.messages]
            )

            ai_output = self.oai_completion(
                messages=[],
                system_prompt=summarize_prompt(user_input=all_chats),
                user_input=None,
            )

            self.state.messages = [Message(role=Role.ASSISTANT, content=ai_output)]

        ai_outputs = [ai_output] if type(ai_output) is str else ai_output

        return {
            "ai_outputs": ai_outputs,
            "state": self.state,
            "current_keywords": (
                current_keywords if len(current_keywords) else self.state.keywords
            ),
        }
