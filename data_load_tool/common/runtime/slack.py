import requests


def send_slack_message(incoming_hook: str, message: str, is_markdown: bool = True) -> None:
    from data_load_tool.common import logger
    from data_load_tool.common.json import json

    """Sends a `message` to  Slack `incoming_hook`, by default formatted as markdown."""
    r = requests.post(
        incoming_hook,
        data=json.dumps({"text": message, "mrkdwn": is_markdown}).encode("utf-8"),
        headers={"Content-Type": "application/json;charset=utf-8"},
    )
    if r.status_code >= 400:
        logger.warning(f"Could not post the notification to slack: {r.status_code}")
    r.raise_for_status()
