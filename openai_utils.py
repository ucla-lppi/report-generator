import os
from openai import OpenAI


def test_openai_api():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API key is not set.")
        return None

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Tell me about OpenAI"}],
            max_tokens=100
        )
        print("OpenAI API key is working.")
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def generate_text(prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "Error with API key. Please set the OPENAI_API_KEY environment variable."

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error generating text: {e}"