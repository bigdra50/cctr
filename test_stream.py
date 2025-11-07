#!/usr/bin/env python3
"""Test streaming debug output."""

import asyncio
import sys
from claude_agent_sdk import query, ClaudeAgentOptions


async def test_stream():
    """Test streaming with debug output."""
    prompt = "Translate 'hello' to Japanese. Output ONLY the translation."

    options = ClaudeAgentOptions(
        model="claude-3-5-haiku-20241022",
        permission_mode="bypassPermissions",
    )

    print("Starting query...", file=sys.stderr, flush=True)

    message_count = 0
    async for message in query(prompt=prompt, options=options):
        message_count += 1
        class_name = message.__class__.__name__
        print(f"\n=== Message #{message_count}: {class_name} ===", file=sys.stderr, flush=True)

        # Print attributes
        if hasattr(message, '__dict__'):
            for key, value in message.__dict__.items():
                print(f"  {key}: {type(value).__name__}", file=sys.stderr, flush=True)

        # Print content for AssistantMessage
        if class_name == 'AssistantMessage' and hasattr(message, 'content'):
            print(f"  Content blocks: {len(message.content)}", file=sys.stderr, flush=True)
            for i, block in enumerate(message.content):
                block_class = block.__class__.__name__
                print(f"    Block {i}: {block_class}", file=sys.stderr, flush=True)
                if hasattr(block, 'text'):
                    print(f"      Text: {block.text}", file=sys.stderr, flush=True)

    print(f"\n=== Total messages: {message_count} ===", file=sys.stderr, flush=True)


if __name__ == "__main__":
    asyncio.run(test_stream())
