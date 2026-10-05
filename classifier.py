import os
from groq import Groq
import json
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#The prompt that gives the LLM instructions on how to classify mails.
CLASSIFICATION_PROMPT = """
You are an email triage classifier. Classify the email into exactly one of: High, Medium, Low.

Definition of High priority (the only test that matters):
"If I don't act on this, I will lose something real and painful — money, an
opportunity, my standing with someone, or access to something I need."
This must be a GENUINE personal stake, not manufactured urgency.

High — ONLY if at least one is true:
- A real deadline with a real consequence (bill due, application closing,
  appointment, contract expiring, exam/submission deadline)
- Financial risk (payment failure, overdraft, fraud alert, refund window closing)
- Security/account risk (suspicious login, account suspension, password reset
  YOU didn't request)
- A specific opportunity that requires a response (job offer, interview
  invite, admission decision, a person waiting on your reply)
- Legal, academic, or institutional consequence for inaction

NOT High, regardless of wording, even if the email uses urgent phrasing,
countdowns, exclamation points, or "act now" language:
- Marketing, promotions, sales, discounts, "limited time offers"
- Betting/gambling platforms (bet closing, odds changing, bonus expiring)
- Social media engagement hooks (streaks, "you were missed", "see who
  viewed you", someone followed/liked/reacted)
- Newsletters, digests, content recommendations
- Generic "don't miss out" / FOMO copy with no real personal stake

If the sender is a marketing, betting, or social-engagement platform, treat
the email as Low or Medium UNLESS it contains one of the genuine High
conditions above (e.g. a security alert from that same platform still
counts). Manufactured urgency from these senders is never High on its own.

Medium — informational mail with no urgent stake: statements, receipts,
newsletters from institutions you have a real relationship with (bank,
employer, university, government), routine replies, confirmations.

Low — pure marketing/promotional content, social notifications, and
anything matching the "not High" list above with no Medium-level
institutional relevance either.

Respond in JSON: {"priority": "High" | "Medium" | "Low", "reason": "<one sentence>"}
"""


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
