"""
Simple message logger that conditionally prints messages based on message ID.
Messages marked as inactive in TERMINAL_MESSAGES.md will not be printed.
"""
from typing import Optional

# Set of inactive message IDs (messages that should not be printed)
INACTIVE_MESSAGE_IDS = {
    26, 27, 28, 29, 30, 31, 32, 33, 34,  # Completion messages
    37, 38, 39, 40, 42, 43, 44,  # Document generation progress
    46, 47,  # AI analysis messages
    51, 52, 53,  # Job Engine Status
    54, 55, 56, 57,  # Research and Search Messages
    67, 68, 69,  # Phase Activation Messages
    75, 76, 77, 78, 79, 80, 81, 82, 83, 84,  # Detailed Progress Messages
    87, 88, 89, 90, 91, 92, 93, 95, 96, 97,  # Application Processing Messages
}


def log_message(message_id: Optional[int], *args, **kwargs) -> None:
    """
    Conditionally print a message based on its ID.
    
    Args:
        message_id: The numeric ID of the message (from TERMINAL_MESSAGES.md).
                   If None, message is always printed.
        *args: Arguments to pass to print()
        **kwargs: Keyword arguments to pass to print()
    
    Usage:
        log_message(26, f"✅ Research file generated: {path}")
        log_message(None, "This message always prints")
    """
    if message_id is None or message_id not in INACTIVE_MESSAGE_IDS:
        print(*args, **kwargs)

