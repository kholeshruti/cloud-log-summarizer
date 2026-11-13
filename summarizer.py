import base64, gzip, json, os, urllib.request
import boto3

sns = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]
API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def lambda_handler(event, context):
    # CloudWatch sends logs base64-encoded and gzipped
    raw = gzip.decompress(base64.b64decode(event["awslogs"]["data"]))
    data = json.loads(raw)
    log_group = data["logGroup"]
    lines = "\n".join(e["message"].strip() for e in data["logEvents"])[:8000]

    prompt = (
        "You are a cloud operations assistant. Summarize these application logs "
        "in under 120 words: what went wrong, likely cause, and one suggested fix.\n\n"
        + lines
    )
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        URL, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            result = json.loads(r.read())
        summary = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        summary = f"AI summary failed ({e}). Raw logs:\n{lines[:1500]}"

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=f"Log summary: {log_group}"[:100],
        Message=f"Log group: {log_group}\n\n{summary}",
    )
    return {"status": "sent"}