"""CLI interface for cctr."""

import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.console import Group
from rich.text import Text

from . import __version__, __build_time__
from .config import Config
from .translator import Translator


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="cctr - Claude-powered CLI translation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate from stdin (auto-detect language)
  echo "Hello, world!" | cctr

  # Translate from command line argument
  cctr "こんにちは、世界！"

  # Specify model
  cctr --model sonnet "Translate this text"

  # Specify target language explicitly
  cctr --to ja "Hello, world!"

  # Show configuration
  cctr --show-config

  # Set native language
  cctr --set-native-lang ja
        """,
    )

    # Input
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to translate (reads from stdin if not provided)",
    )

    # Translation options
    parser.add_argument(
        "--to",
        dest="target_language",
        help="Target language code (e.g., en, ja, zh)",
    )

    parser.add_argument(
        "--from",
        dest="source_language",
        help="Source language code (auto-detected if not provided)",
    )

    # Model options
    parser.add_argument(
        "--model",
        "-m",
        help="Model to use (haiku, sonnet, opus, or full model name)",
    )

    # Configuration
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration",
    )

    parser.add_argument(
        "--set-native-lang",
        metavar="LANG",
        help="Set native language in configuration",
    )

    parser.add_argument(
        "--set-default-model",
        metavar="MODEL",
        help="Set default model in configuration",
    )

    # Version
    parser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Show version information",
    )

    # Debug options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress messages",
    )

    return parser


def show_version() -> None:
    """Show version information."""
    print(f"cctr version {__version__}")
    print(f"Build time: {__build_time__}")


def show_config(config: Config) -> None:
    """Show current configuration."""
    print("Current Configuration:")
    print(f"  Config file: {config.config_file}")
    print(f"  Native language: {config.native_language}")
    print(f"  Default model: {config.default_model}")


def debug_print(message: str, debug: bool = False) -> None:
    """Print debug message to stderr."""
    if debug:
        print(f"DEBUG: {message}", file=sys.stderr, flush=True)


def progress_print(message: str, quiet: bool = False) -> None:
    """Print progress message to stderr."""
    if not quiet:
        print(message, file=sys.stderr, flush=True)


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    debug_print("Starting cctr", args.debug)
    debug_print(f"Arguments: {args}", args.debug)

    # Handle version command
    if args.version:
        show_version()
        return 0

    # Load configuration
    debug_print("Loading configuration", args.debug)
    config = Config()
    debug_print(f"Config: native_language={config.native_language}, model={config.default_model}", args.debug)

    # Handle configuration commands
    if args.show_config:
        show_config(config)
        return 0

    if args.set_native_lang:
        config.native_language = args.set_native_lang
        print(f"Native language set to: {args.set_native_lang}")
        return 0

    if args.set_default_model:
        config.default_model = args.set_default_model
        print(f"Default model set to: {args.set_default_model}")
        return 0

    # Get input text
    debug_print("Getting input text", args.debug)
    if args.text:
        text = args.text
        debug_print(f"Input from argument: '{text}'", args.debug)
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("Error: No input text provided", file=sys.stderr)
            print("Usage: cctr <text> or echo <text> | cctr", file=sys.stderr)
            return 1
        debug_print("Reading from stdin", args.debug)
        text = sys.stdin.read().strip()
        debug_print(f"Input from stdin: '{text}'", args.debug)

    if not text:
        print("Error: Empty input text", file=sys.stderr)
        return 1

    # Get model for translator
    model = args.model or config.default_model
    debug_print(f"Using model: {model}", args.debug)

    # Translate
    try:
        # Show spinner while translating
        console = Console(file=sys.stderr)

        if args.quiet:
            # No spinner in quiet mode
            translator_quiet = Translator(model=model, debug=args.debug, quiet=args.quiet)
            if args.target_language:
                # Explicit target language
                debug_print(f"Translating to: {args.target_language}", args.debug)
                result = translator_quiet.translate(
                    text,
                    target_language=args.target_language,
                    source_language=args.source_language,
                )
            else:
                # Auto-detect and translate
                debug_print(f"Auto-translating with native language: {config.native_language}", args.debug)
                result = translator_quiet.auto_translate(text, config.native_language)
        else:
            # State for progress updates
            progress_messages = []

            def progress_callback(message: str, cost: Optional[float]) -> None:
                """Update progress display."""
                progress_messages.clear()
                progress_messages.append(Text(f"  {message}", style="dim"))

                # Update live display
                spinner = Spinner("dots", text="Translating...", style="cyan")
                if progress_messages:
                    display = Group(spinner, *progress_messages)
                else:
                    display = spinner
                live.update(display)

            # Show animated spinner with progress updates
            spinner = Spinner("dots", text="Translating...", style="cyan")
            with Live(spinner, console=console, transient=True) as live:
                # Create translator with progress callback
                translator_with_progress = Translator(
                    model=model,
                    debug=args.debug,
                    quiet=args.quiet,
                    progress_callback=progress_callback,
                )

                if args.target_language:
                    # Explicit target language
                    debug_print(f"Translating to: {args.target_language}", args.debug)
                    result = translator_with_progress.translate(
                        text,
                        target_language=args.target_language,
                        source_language=args.source_language,
                    )
                else:
                    # Auto-detect and translate
                    debug_print(f"Auto-translating with native language: {config.native_language}", args.debug)
                    result = translator_with_progress.auto_translate(text, config.native_language)

            # Show completion message
            console.print("✓ Translation complete", style="green")

        debug_print(f"Translation completed: '{result}'", args.debug)

        # Output to stdout
        print(result, flush=True)
        return 0

    except Exception as e:
        print(f"\nTranslation error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
