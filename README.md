# cctr

Claude-powered CLI translation tool with animated progress display

## Features

- 🚀 Simple CLI interface for quick translations
- ✨ Animated spinner with real-time progress updates
- 🔄 Auto-detect source language and translate intelligently
- 🎯 Support for multiple languages (English, Japanese, Chinese, Korean, and more)
- ⚙️ XDG Base Directory compliant configuration
- 🤖 Powered by Claude AI via Claude Agent SDK (Haiku, Sonnet, or Opus models)
- 🔐 Works with Claude Code subscription (no API key required)
- 📦 Easy to use with `uvx` (no installation required)
- 📋 Clipboard integration support

## Prerequisites

### Claude Code Installation

This tool requires Claude Code 2.0.0 or higher:

```bash
npm install -g @anthropic-ai/claude-code
```

### Authentication

Authentication is handled by Claude Code itself. You have two options:

1. **Claude Code Subscription** (Recommended)
   - If you have a Claude Code subscription, no additional setup is needed
   - The tool will use Claude Code's existing authentication

2. **API Key** (Optional)
   - Alternatively, you can use an Anthropic API key
   - Set the environment variable:
     ```bash
     export ANTHROPIC_API_KEY="your-api-key-here"
     ```

## Installation

### Using uvx (Recommended)

```bash
# Run directly from GitHub (no clone required)
uvx --from git+https://github.com/bigdra50/cctr cctr 'Hello, world!'

# Or from local directory
uvx --from . cctr 'Hello, world!'

# Or if published to PyPI
uvx cctr 'Hello, world!'
```

### Using uv

```bash
# Install with uv
uv pip install .

# Or install in development mode
uv pip install -e .
```

### From source

```bash
# Clone the repository
git clone https://github.com/bigdra50/cctr
cd cctr

# Install dependencies and the package
uv sync
uv pip install -e .
```

## Quick Start

### No Installation Required

```bash
# Run directly from GitHub without cloning
uvx --from git+https://github.com/bigdra50/cctr cctr 'Hello, world!'
# Output: こんにちは、世界！
```

### Basic Translation

```bash
# Translate from command line argument
cctr 'Hello, world!'
# Output: こんにちは、世界！

# Translate from stdin
echo 'こんにちは、世界！' | cctr
# Output: Hello, world!

# Translate with explicit target language
cctr --to ja 'Hello, world!'

# Use a different model
cctr --model sonnet 'Translate this text'
```

### Clipboard Integration

```bash
# Translate text from clipboard
pbpaste | cctr

# Translate and copy result back to clipboard
pbpaste | cctr | pbcopy

# Convenient aliases (add to .zshrc or .bashrc)
alias ct='pbpaste | cctr'                # Translate clipboard
alias ctt='pbpaste | cctr | pbcopy'      # Translate and copy back
```

### Configuration

```bash
# Show current configuration
cctr --show-config

# Set your native language (used for auto-translation)
cctr --set-native-lang ja

# Set default model
cctr --set-default-model haiku
```

## Usage

### Command Line Options

```
Options:
  text                    Text to translate (reads from stdin if not provided)
  --to LANG              Target language code (e.g., en, ja, zh)
  --from LANG            Source language code (auto-detected if not provided)
  --model, -m MODEL      Model to use (haiku, sonnet, opus)
  --show-config          Show current configuration
  --set-native-lang LANG Set native language in configuration
  --set-default-model    Set default model in configuration
  --debug                Enable debug output
  --quiet, -q            Suppress progress messages
  --version, -v          Show version information
  -h, --help             Show help message
```

### Progress Display

The tool shows animated progress with real-time updates:

```
⠋ Translating...
  Translating: こんに...          ← Real-time preview

⠙ Translating...
  Using tool: Bash                ← Tool usage notification

✓ Translation complete (Cost: $0.001217)  ← Completion with cost
```

Use `--quiet` to suppress all progress messages:
```bash
cctr --quiet 'Hello, world!'
```

### Auto-Translation Logic

1. **Language Detection**: Automatically detects the source language
2. **Smart Translation**:
   - If the detected language is your native language → translates to English
   - If the detected language is NOT your native language → translates to your native language

Example with `native_language=ja`:
```bash
cctr 'Hello, world!'        # → こんにちは、世界！
cctr 'こんにちは、世界！'    # → Hello, world!
```

### Supported Languages

- English (en)
- Japanese (ja)
- Chinese (zh)
- Korean (ko)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)

### Available Models

| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| haiku | ⚡⚡⚡ | 💰 | ⭐⭐ | Quick translations, simple text |
| sonnet | ⚡⚡ | 💰💰 | ⭐⭐⭐ | General purpose, balanced |
| opus | ⚡ | 💰💰💰 | ⭐⭐⭐⭐ | Complex/technical content |

Model aliases:
- `haiku` → claude-3-5-haiku-20241022
- `sonnet` → claude-3-5-sonnet-20241022
- `opus` → claude-opus-4-20250514

## Advanced Examples

### Pipe Integration

```bash
# Translate file contents
cat input.txt | cctr

# Translate git commit messages
git log --oneline -1 --format=%s | cctr

# Translate curl output
curl https://example.com | cctr

# Chain with other commands
echo 'Hello' | cctr | wc -c
```

### Batch Translation

```bash
# Translate multiple files
for file in *.txt; do
  echo "Translating $file..."
  cctr < "$file" > "translated_$file"
done
```

### Shell Script Integration

```bash
#!/bin/bash

# User input translation
read -p "Enter text: " text
translated=$(echo "$text" | cctr)
echo "Translated: $translated"
```

## Configuration File

Configuration is stored in XDG-compliant location:

```
~/.config/cctr/config.yaml
```

Example configuration:

```yaml
native_language: ja
default_model: haiku
```

You can edit this file manually or use the CLI commands:
```bash
cctr --set-native-lang ja
cctr --set-default-model sonnet
```

## Troubleshooting

### Special Characters in Input

When using special characters like `!` in your input, use one of these methods:

**Method 1: Single quotes (Recommended)**
```bash
cctr 'Hello World!!!!!'
```

**Method 2: Pipe input**
```bash
echo 'Hello World!!!!!' | cctr
```

**Method 3: Escape characters**
```bash
cctr "Hello World\!\!\!\!\!"
```

**Why?** In some shells (bash, zsh with `HIST_EXPAND`), `!` triggers history expansion even inside double quotes.

### Empty Input

```bash
# Error example
echo '' | cctr
# Error: Empty input text
```

Ensure your input has actual content.

### Authentication Errors

If you encounter authentication errors:

1. **Check Claude Code Subscription**
   - Visit https://claude.ai and verify login status
   - Ensure subscription is active

2. **Or Set API Key**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"

   # Or add to .bashrc / .zshrc
   echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
   ```

### Performance

- First execution may take 10-15 seconds (Claude Code CLI startup)
- Subsequent executions are faster due to caching
- Typical translation times:
  - **Haiku**: < 1 second
  - **Sonnet**: 1-3 seconds
  - **Opus**: 3-5 seconds

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
pytest

# Format code (line length: 100)
black src/

# Lint code
ruff src/

# Run with debug output
cctr --debug 'test text'
```

## Tips

1. **Pipeline Integration**: Use with `curl`, `cat`, `git` commands
2. **Aliases**: Set up convenient aliases
   ```bash
   alias t='cctr'
   alias tja='cctr --to ja'
   alias ten='cctr --to en'
   alias ct='pbpaste | cctr'
   alias ctt='pbpaste | cctr | pbcopy'
   ```
3. **Model Selection**: Use haiku for simple text, sonnet for technical content
4. **Quiet Mode**: Use `--quiet` in scripts to suppress progress messages

## License

MIT License

## Author

bigdra50
