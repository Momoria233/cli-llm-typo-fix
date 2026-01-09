import sys
import typer
import pyperclip
from typing import Optional, List
from typing_extensions import Annotated
from .llm import fix_text, list_models
from .config import save_config, load_config

typer_app = typer.Typer(
    help="Fix typos in the provided TEXT or from stdin.",
    context_settings={"help_option_names": ["-h", "--help"]}
)

@typer_app.command()
def config(
    api_key: Annotated[Optional[str], typer.Option("--api-key", help="Set OpenAI API key")] = None,
    model: Annotated[Optional[str], typer.Option("--model", help="Set OpenAI model")] = None,
    base_url: Annotated[Optional[str], typer.Option("--base-url", help="Set OpenAI API base URL")] = None,
    list_models_flag: Annotated[bool, typer.Option("--list", help="List available models from OpenAI API")] = False,
):
    """
    Configure API key and model settings.
    """
    config_data = load_config()
    
    if api_key:
        config_data["api_key"] = api_key
        typer.echo(f"API key updated.")
        
    if model:
        config_data["model"] = model
        typer.echo(f"Model updated to {model}.")
        
    if base_url:
        config_data["base_url"] = base_url
        typer.echo(f"Base URL updated to {base_url}.")
    
    if list_models_flag:
        try:
            models = list_models()
            typer.echo("Available Models:")
            for m in models:
                typer.echo(f"- {m}")
        except Exception as e:
            typer.echo(f"Error listing models: {str(e)}")
        
    if not api_key and not model and not base_url and not list_models_flag:
        typer.echo("Current Configuration:")
        typer.echo(f"API Key: {'*' * 8 + config_data['api_key'][-4:] if config_data['api_key'] else 'Not set'}")
        typer.echo(f"Model: {config_data['model']}")
        typer.echo(f"Base URL: {config_data.get('base_url', 'Default')}")
            
    save_config(config_data)

@typer_app.command(
    name="fix",
    help="Fix typos in the provided TEXT or from stdin.",
    epilog="Commands:\n  config   Configure API key and settings."
)
def fix(
    text: Annotated[Optional[List[str]], typer.Argument(help="The text to fix typos in.")] = None,
    suggest: Annotated[bool, typer.Option("--suggest", help="Suggest improvements instead of just fixing.")] = False,
    rewrite: Annotated[bool, typer.Option("--rewrite", help="Rewrite the text completely.")] = False,
):
    """
    Fix typos in the provided TEXT or from stdin.
    """
    # Determine mode
    mode = "fix"
    if rewrite:
        mode = "rewrite"
    elif suggest:
        mode = "suggest"

    # Input handling logic
    input_text = ""
    if text:
        input_text = " ".join(text)
    
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
            sys.exit(1)

    # Clean up input and check for empty string
    if not input_text or not input_text.strip():
         typer.echo("Empty text provided.")
         sys.exit(1)

    result = fix_text(input_text, mode=mode)
    
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

def app():
    """
    Entry point for the CLI. Handles default command logic using sys.argv injection.
    """
    known_commands = ["config"]
    
    # Check if first arg is a known command
    # sys.argv[0] is script name
    if len(sys.argv) == 1:
        # No args provided, default to 'fix' which handles stdin check
        sys.argv.insert(1, "fix")
    elif sys.argv[1] not in known_commands:
        # If it's not 'config', treat it as args for 'fix'
        # UNLESS it's --help, in which case we let Typer handle it?
        # NO, user wants 'typofix --help' to show usage (fix usage) + config existence.
        # If we inject 'fix', 'typofix --help' becomes 'typofix fix --help'.
        # This shows 'fix' usage. We added 'epilog' to 'fix' to mention 'config'.
        # So yes, inject 'fix' even for --help.
        sys.argv.insert(1, "fix")
        
    typer_app()

if __name__ == "__main__":
    app()
