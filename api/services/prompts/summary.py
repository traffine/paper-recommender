from core.config import SUMMARY_WORD_LIMIT


def summarize_prompt(user_input: str) -> str:
    prompt = f"""
    <入力文>を{SUMMARY_WORD_LIMIT}文字以内で回答してください。

    <入力文>
    {user_input}
    """
    return prompt
