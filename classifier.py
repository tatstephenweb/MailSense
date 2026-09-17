import os
from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def test_groq_connection():
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": "Say hello in one word."}
        ]
    )
    print(response.choices[0].message.content)


CLASSIFICATION_PROMPT = """You are an email prioritization assistant. You will be given the sender, subject, and body of an email. Classify it as High or Medium priority.

Classify it as High if ANY ONE of the following is true:
(1) the email contains an explicit deadline or date,
(2) the email contains urgent language such as 'urgent' or 'reply immediately',
(3) the email implies the recipient must take action.
These conditions are independent — one alone is enough to qualify as High.

If none of these apply, classify it as Medium — this includes purely informational emails from organizations such as banks, employers, universities, or government bodies, as well as ordinary non-urgent correspondence.

Respond ONLY with valid JSON in this exact format, with no extra text:
{"priority": "High" or "Medium", "reason": "one short sentence explaining the classification"}"""


def classify_email(sender, subject, body):
    truncated_body = body[:2000]

    user_content = f"Sender: {sender}\nSubject: {subject}\nBody: {truncated_body}"

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": CLASSIFICATION_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        return {
            "priority": result.get("priority", "Medium"),
            "reason": result.get("reason", "")
        }

    except Exception as e:
        print(f"Classification failed: {e}")
        return {"priority": "Medium", "reason": "Classification failed, defaulted to Medium"}
