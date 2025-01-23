from openai import OpenAI
import os


def create_completion_openai(
    model="gpt-4o",
    system_prompt="You are a helpful assistant.",
    user_prompt="Write a haiku about recursion in programming.",
    api_key=os.getenv("OPENAI_API_KEY")
):
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    )
    return completion.choices[0].message.content
