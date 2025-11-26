#!/usr/bin/env python3
"""
SMS to Telegram Forwarder.

This script is called by gammu-smsd when a new SMS is received.
It reads the SMS content from environment variables and forwards
the message to a Telegram chat via the Telegram Bot API.
"""

import logging
import os
import sys
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def get_env_var(name: str, required: bool = True) -> Optional[str]:
    """
    Get an environment variable value.

    Args:
        name: The name of the environment variable.
        required: If True, raises an error when the variable is missing.

    Returns:
        The value of the environment variable or None if not set.

    Raises:
        SystemExit: If a required environment variable is not set.
    """
    value = os.environ.get(name)
    if required and not value:
        logger.error("Required environment variable '%s' is not set", name)
        sys.exit(1)
    return value


def get_sms_text() -> str:
    """
    Extract SMS text from environment variables.

    Gammu SMSD sets DECODED_PARTS to indicate the number of message parts.
    If DECODED_PARTS is 0, the message is in SMS_1_TEXT.
    Otherwise, the message is split across DECODED_N_TEXT variables.

    Returns:
        The complete SMS text content.
    """
    decoded_parts_str = os.environ.get("DECODED_PARTS", "0")
    try:
        numparts = int(decoded_parts_str)
    except ValueError:
        logger.warning(
            "Invalid DECODED_PARTS value: '%s', defaulting to 0", decoded_parts_str
        )
        numparts = 0

    if numparts == 0:
        # Single-part message
        return os.environ.get("SMS_1_TEXT", "")

    # Multi-part message - concatenate all parts
    text_parts = []
    for i in range(1, numparts + 1):
        varname = f"DECODED_{i}_TEXT"
        part = os.environ.get(varname, "")
        text_parts.append(part)

    return "".join(text_parts)


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    text: str,
    proxy: Optional[str] = None,
) -> bool:
    """
    Send a message to Telegram.

    Args:
        bot_token: Telegram Bot API token.
        chat_id: Target Telegram chat ID.
        text: Message text to send.
        proxy: Optional HTTP/HTTPS proxy URL.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.post(api_url, json=payload, proxies=proxies, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("ok"):
            logger.info("Message sent successfully to chat %s", chat_id)
            return True
        logger.error("Telegram API error: %s", result)
        return False
    except requests.exceptions.Timeout:
        logger.error("Request to Telegram API timed out")
        return False
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send message to Telegram: %s", e)
        return False


def main() -> int:
    """
    Main function to process received SMS and forward to Telegram.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    # Get required configuration
    bot_token = get_env_var("BOT_TOKEN")
    chat_id = get_env_var("CHAT_ID")
    proxy = get_env_var("PROXY", required=False)

    # Get sender number and message text
    sender_number = os.environ.get("SMS_1_NUMBER", "Unknown")
    sms_text = get_sms_text()

    if not sms_text:
        logger.warning("Received empty SMS from %s", sender_number)

    # Format message for Telegram
    message = f"`Message from {sender_number}:`\n{sms_text}"

    logger.info("Forwarding SMS from %s to Telegram", sender_number)

    # Send to Telegram
    if send_telegram_message(bot_token, chat_id, message, proxy):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
