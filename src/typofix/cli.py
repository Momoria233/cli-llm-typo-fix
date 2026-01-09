import sys
import typer
import pyperclip
from typing import Optional, List
from typing_extensions import Annotated
from .llm import fix_text
from .config import save_config, load_config, RECOMMENDED_MODELS

app = typer.Typer(
    help="Fix typos in the provided TEXT or from stdin.",
    context_settings={"help_option_names": ["-h", "--help"], "allow_extra_args": True}
)

@app.command()
def config(
    api_key: Annotated[Optional[str], typer.Option("--api-key", help="Set OpenAI API key")] = None,
    model: Annotated[Optional[str], typer.Option("--model", help="Set OpenAI model")] = None,
):
    """
    Configure API key and model settings.
    """
    config_data = load_config()
    
    if api_key:
        config_data["api_key"] = api_key
        typer.echo(f"API key updated.")
        
    if model:
        if model not in RECOMMENDED_MODELS:
            typer.echo(f"Warning: {model} is not in the recommended list: {', '.join(RECOMMENDED_MODELS)}")
        config_data["model"] = model
        typer.echo(f"Model updated to {model}.")
        
    if not api_key and not model:
        typer.echo("Current Configuration:")
        typer.echo(f"API Key: {'*' * 8 + config_data['api_key'][-4:] if config_data['api_key'] else 'Not set'}")
        typer.echo(f"Model: {config_data['model']}")
        typer.echo("\nRecommended Models:")
        for m in RECOMMENDED_MODELS:
            typer.echo(f"- {m}")
            
    save_config(config_data)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    suggest: Annotated[bool, typer.Option("--suggest", help="Suggest improvements instead of just fixing.")] = False,
    rewrite: Annotated[bool, typer.Option("--rewrite", help="Rewrite the text completely.")] = False,
    test: Annotated[bool, typer.Option("--test", help="Test with stub responses instead of real API calls.")] = False,
):
    """
    Fix typos in the provided TEXT or from stdin.
    """
    if ctx.invoked_subcommand is not None:
        return

    # Determine mode
    mode = "fix"
    if rewrite:
        mode = "rewrite"
    elif suggest:
        mode = "suggest"

    # Input handling logic
    # Typer puts extra arguments (like the text) in ctx.args because allow_extra_args=True
    text_parts = ctx.args
    input_text = ""
    if text_parts:
        input_text = " ".join(text_parts)
    
    if not input_text:
        # Check if there is data in stdin (piped input)
        # isatty() returns True if the stream is interactive (connected to a terminal device)
        # It returns False if it's a pipe or file redirection.
        if not sys.stdin.isatty():
            # Read all input from stdin
            input_text = sys.stdin.read().strip()
        else:
            # Interactive mode but no argument provided
            typer.echo("No text provided. Please provide text as an argument or via stdin.")
            # raise typer.Exit(code=1) # Callback cannot raise Exit(code=1) cleanly?
            # It can, but let's just exit.
            sys.exit(1)

    # Clean up input and check for empty string
    if not input_text or not input_text.strip():
         typer.echo("Empty text provided.")
         sys.exit(1)

    result = fix_text(input_text, mode=mode, test=test)
    
    # Handle config error / missing API key
    if result.startswith("[CONFIG_NEEDED]"):
        # Remove the internal prefix and show friendly message
        friendly_msg = result.replace("[CONFIG_NEEDED] ", "")
        typer.echo(friendly_msg)
        return

    if result.startswith("Error:"):
        typer.echo(result)
        sys.exit(1)
    
    if mode == "fix":
        typer.echo(result)    
        pyperclip.copy(result)
        typer.echo("Copied to clipboard!", err=True)
    elif mode == "suggest":
        typer.echo(result)
    elif mode == "rewrite":
        # Interactive selection for rewrite mode
        typer.echo(result)
        
        # Parse lines to find options (assuming numbered list format "1. ...")
        lines = result.strip().split('\n')
        options = []
        for line in lines:
            # Simple parsing: look for lines starting with a number and a dot
            parts = line.split('.', 1)
            if len(parts) > 1 and parts[0].strip().isdigit():
                options.append(parts[1].strip())
        
        if options:
            choice = typer.prompt(f"Select an option (1-{len(options)})", type=int)
            if 1 <= choice <= len(options):
                selected_text = options[choice - 1]
                pyperclip.copy(selected_text)
                typer.echo(f"Option {choice} copied to clipboard!", err=True)
            else:
                typer.echo("Invalid selection.")
        else:
            # Fallback if parsing fails
            typer.echo("Could not parse options for selection.")

if __name__ == "__main__":
    app()
