# typofix

A cross-platform CLI tool to fix typos using LLM.

## Installation

```bash
pip install -e .
```

## Usage

### As an argument

```bash
typofix "Helo world"
# Output: [Fixed] Helo world
```

### From stdin

```bash
echo "Helo world" | typofix
# Output: [Fixed] Helo world
```
