# typofix

A cross-platform CLI tool to fix typos and improve text with an LLM.

- Default behavior: `typofix <TEXT>` runs typo-fixing (no subcommand needed).
- Extra modes: `--suggest` (suggest improvements + reasons), `--rewrite` (rewrite alternatives).
- Clipboard: in default fix mode, the final text is copied to clipboard.

## Requirements

- Python: >= 3.9

## Installation

### Local (recommended for development)

```bash
pip install -e .
```

### Regular install (from a source checkout)

```bash
pip install .
```

## Quickstart

1) Configure API key and (optionally) model:

```bash
typofix config --api-key YOUR_KEY
# optional:
typofix config --model gpt-4o-mini
```

2) Fix a sentence:

```bash
typofix "Helo world"
```

## Usage

### Default (fix)

Fix grammar/typos with minimal changes.

```bash
typofix "这是一段可能由语病的测试"
```

The output is also copied to clipboard in fix mode.

### Suggest improvements (with explanations)

Gives prioritized suggestions and brief reasons. Output is in Chinese if input is Chinese; in English if input is English.

```bash
typofix --suggest "This sentence have a problem."
```

### Rewrite

Provides 2–3 rewritten alternatives.

```bash
typofix --rewrite "帮我把这句话写得更自然一点"
```

### From stdin (pipes)

```bash
echo "Helo world" | typofix
```

### Help

`typofix --help` shows the default command help. Configuration is available as a command:

```bash
typofix config --help
```

## Configuration

Configuration is stored under your home directory (JSON). You can always re-run the config command to update values.

### Set / view configuration

```bash
typofix config
```

### Set model

```bash
typofix config --model gpt-4o-mini
```

### List available models

Lists models available to your API key (and the configured base URL).

```bash
typofix config --list
```

### Use an OpenAI-compatible provider (base URL)

This tool supports OpenAI-compatible APIs by configuring `--base-url`.

Example (DashScope compatible mode):

```bash
typofix config --base-url https://dashscope.aliyuncs.com/compatible-mode/v1
# then set provider key + model

typofix config --api-key YOUR_PROVIDER_KEY

typofix config --model qwen-plus
```

Switch back to OpenAI:

```bash
typofix config --base-url https://api.openai.com/v1
```

## Troubleshooting

- "API key not configured": run `typofix config --api-key YOUR_KEY`.
- "No such command '<text>'": your installed entry point may be outdated. Reinstall with `pip install -e .` from the repo root.
- Model list fails: verify `--base-url` and `--api-key` are correct for your provider.

