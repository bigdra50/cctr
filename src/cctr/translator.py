"""Translation core functionality using Claude Agent SDK."""

import asyncio
import sys
from typing import Callable, Optional

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
)


class LanguageDetector:
    """Detect the language of input text."""

    @staticmethod
    def detect(text: str) -> str:
        """
        Detect language of the given text.

        Simple heuristic-based detection:
        - If contains Japanese characters (Hiragana, Katakana, Kanji), return 'ja'
        - Otherwise, return 'en'
        """
        # Check for Japanese characters
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FFF),  # CJK Unified Ideographs (Kanji)
        ]

        for char in text:
            code = ord(char)
            for start, end in japanese_ranges:
                if start <= code <= end:
                    return "ja"

        return "en"


class Translator:
    """Translation service using Claude Agent SDK."""

    # Model aliases
    MODEL_ALIASES = {
        "haiku": "claude-3-5-haiku-20241022",
        "sonnet": "claude-3-5-sonnet-20241022",
        "opus": "claude-opus-4-20250514",
    }

    # Language code to full name mapping
    LANGUAGE_NAMES = {
        "en": "English",
        "ja": "Japanese",
        "zh": "Chinese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
    }

    def __init__(
        self,
        model: str = "haiku",
        debug: bool = False,
        quiet: bool = False,
        progress_callback: Optional[Callable[[str, Optional[float]], None]] = None,
    ):
        """
        Initialize Translator.

        Args:
            model: Model name or alias (haiku, sonnet, opus)
            debug: Enable debug output
            quiet: Suppress progress messages
            progress_callback: Callback function for progress updates (message, cost)

        Note:
            Authentication is handled by Claude Code itself.
            No API key is required if Claude Code is authenticated
            (via subscription or API key).
        """
        self.model = self._resolve_model(model)
        self.debug = debug
        self.quiet = quiet
        self.progress_callback = progress_callback

    def _resolve_model(self, model: str) -> str:
        """Resolve model alias to full model name."""
        return self.MODEL_ALIASES.get(model, model)

    def _get_language_name(self, code: str) -> str:
        """Get full language name from language code."""
        return self.LANGUAGE_NAMES.get(code, code)

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> str:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detected if not provided)

        Returns:
            Translated text
        """
        # Auto-detect source language if not provided
        if source_language is None:
            source_language = LanguageDetector.detect(text)

        target_lang_name = self._get_language_name(target_language)
        source_lang_name = self._get_language_name(source_language)

        # Build prompt
        prompt = f"""Translate the following text from {source_lang_name} to {target_lang_name}.
Output ONLY the translation, without any explanations, comments, or additional text.

Text to translate:
{text}"""

        if self.debug:
            print(f"DEBUG: About to call _translate_async", file=sys.stderr, flush=True)

        # Call Claude Agent SDK
        result = asyncio.run(self._translate_async(prompt))

        if self.debug:
            print(f"DEBUG: _translate_async returned: {result}", file=sys.stderr, flush=True)

        return result

    async def _translate_async(self, prompt: str) -> str:
        """
        Async translation using Claude Agent SDK with streaming progress.

        Args:
            prompt: Translation prompt

        Returns:
            Translated text
        """
        options = ClaudeAgentOptions(
            model=self.model,
            permission_mode="bypassPermissions",  # Auto-approve tool use for translation
        )

        # Collect all assistant messages
        assistant_messages = []
        message_count = 0
        tool_uses = []
        total_cost = None
        accumulated_text = ""  # For streaming preview

        async with ClaudeSDKClient(options=options) as client:
            # Send query
            await client.query(prompt)

            # Receive and process messages
            async for message in client.receive_messages():
                message_count += 1
                class_name = message.__class__.__name__

                # Debug: Output detailed stream information
                if self.debug:
                    print(f"\n[DEBUG] Message #{message_count}: {class_name}", file=sys.stderr, flush=True)

                # Process AssistantMessage
                if isinstance(message, AssistantMessage):
                    text_blocks = []
                    for block in message.content:
                        # Handle text blocks
                        if isinstance(block, TextBlock):
                            text_blocks.append(block.text)
                            accumulated_text += block.text

                            # Send progress update via callback
                            if self.progress_callback and not self.quiet:
                                preview = accumulated_text.strip()
                                if len(preview) > 50:
                                    preview = preview[:47] + "..."
                                self.progress_callback(f"Translating: {preview}", None)

                            if self.debug:
                                preview = block.text[:50] + "..." if len(block.text) > 50 else block.text
                                print(f"  [TEXT] {preview}", file=sys.stderr, flush=True)

                        # Handle tool use blocks
                        elif isinstance(block, ToolUseBlock):
                            tool_uses.append(block.name)

                            # Send tool usage update via callback
                            if self.progress_callback and not self.quiet:
                                self.progress_callback(f"Using tool: {block.name}", None)

                            if self.debug:
                                print(f"\n  [TOOL] {block.name} (id: {block.id})", file=sys.stderr, flush=True)
                                if block.name == "Bash" and hasattr(block, 'input'):
                                    cmd = block.input.get('command', '')
                                    print(f"    Command: {cmd}", file=sys.stderr, flush=True)

                    if text_blocks:
                        assistant_messages.append("".join(text_blocks))

                # Process ResultMessage (completion indicator)
                elif isinstance(message, ResultMessage):
                    if hasattr(message, 'total_cost_usd') and message.total_cost_usd:
                        total_cost = message.total_cost_usd

                    # Send completion update via callback
                    if self.progress_callback and not self.quiet:
                        if total_cost and total_cost > 0:
                            self.progress_callback(f"Translation complete (Cost: ${total_cost:.6f})", total_cost)
                        else:
                            self.progress_callback("Translation complete", total_cost)

                    if self.debug:
                        print(f"\n  [RESULT] Translation complete", file=sys.stderr, flush=True)
                        if total_cost:
                            print(f"  [COST] ${total_cost:.6f}", file=sys.stderr, flush=True)

                    break  # Exit loop on result

                # Process UserMessage (may contain tool results)
                elif isinstance(message, UserMessage):
                    if self.debug:
                        print(f"  [USER] User message received", file=sys.stderr, flush=True)

        if self.debug:
            print(f"\n[DEBUG] Total messages: {message_count}", file=sys.stderr, flush=True)
            if tool_uses:
                print(f"[DEBUG] Tools used: {', '.join(tool_uses)}", file=sys.stderr, flush=True)

        # Return the last assistant message (final translation)
        return assistant_messages[-1].strip() if assistant_messages else ""

    def auto_translate(self, text: str, native_language: str) -> str:
        """
        Automatically translate text based on detected language.

        If the detected language matches native_language, translate to English.
        Otherwise, translate to native_language.

        Args:
            text: Text to translate
            native_language: User's native language code

        Returns:
            Translated text
        """
        detected_lang = LanguageDetector.detect(text)

        if detected_lang == native_language:
            target_language = "en"
        else:
            target_language = native_language

        return self.translate(text, target_language, detected_lang)
