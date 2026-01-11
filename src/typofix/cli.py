import sys
import typer
import pyperclip
import subprocess
import shutil
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
        typer.echo(f"API Key: {'*' * 8 + config_data['api_key'][-4:] if config_data.get('api_key') else 'Not set'}")
        typer.echo(f"Model: {config_data.get('model', 'Not set')}")
        typer.echo(f"Base URL: {config_data.get('base_url', 'Default')}")
            
    save_config(config_data)

@typer_app.command()
def setup():
    typer.echo("Welcome to typofix configuration wizard!")
    typer.echo("We'll set up your API credentials and preferences.\n")

    current_config = load_config()

    typer.echo("1. API Base URL")
    typer.echo("   The endpoint for the LLM API (e.g., https://api.openai.com/v1).")
    base_url = typer.prompt("   Base URL", default=current_config.get("base_url", "https://api.openai.com/v1"))

    typer.echo("\n2. API Key")
    typer.echo("   Your authentication key for the provider.")
    
    api_key_prompt = "   API Key"
    if current_config.get("api_key"):
        api_key_prompt += " (Leave empty to keep current)"
    
    api_key = typer.prompt(api_key_prompt, hide_input=True, default="", show_default=False)
    
    if not api_key and current_config.get("api_key"):
        api_key = current_config["api_key"]

    typer.echo("\n3. Model")
    typer.echo("   The name of the LLM model to use (e.g., gpt-4o-mini).")
    
    typer.echo("   Fetching available models...")
    try:
        models = list_models(api_key=api_key, base_url=base_url)
        typer.echo("   Available models:")
        for m in models:
            typer.echo(f"   - {m}")
    except Exception as e:
        typer.echo("   ⚠️ Could not fetch models automatically.")
        typer.echo("   (Check your API Key, Base URL, or network connection)")
        typer.echo(f"   Error details: {str(e)}")
        typer.echo("   Please enter the model name manually.")

    model = typer.prompt("   Model", default=current_config.get("model", "gpt-4o-mini"))

    config_data = current_config.copy()
    config_data.update({
        "api_key": api_key,
        "base_url": base_url,
        "model": model
    })
    
    save_config(config_data)
    
    typer.echo("\nConfiguration saved successfully!")
    
    typer.echo("\n" + "="*30)
    typer.echo("How to use typofix:")
    typer.echo("1. Default (Fix):   typofix \"text with typos\"")
    typer.echo("2. Suggest Mode:    typofix --suggest \"text with typos\"")
    typer.echo("3. Rewrite Mode:    typofix --rewrite \"text with typos\"")
    typer.echo("4. Piped Input:     echo \"typos\" | typofix")
    typer.echo("="*30 + "\n")

def copy_to_clipboard(text: str) -> bool:
    success = False
    try:
        pyperclip.copy(text)
        success = True
    except Exception:
        if sys.platform == "darwin":
            try:
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate(input=text.encode('utf-8'))
                success = (process.returncode == 0)
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            commands = [
                (['wl-copy'], {}),
                (['xclip', '-selection', 'clipboard'], {}),
                (['xsel', '--clipboard', '--input'], {})
            ]
            
            for cmd_args, kwargs in commands:
                if shutil.which(cmd_args[0]):
                    try:
                        process = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
                        process.communicate(input=text.encode('utf-8'))
                        if process.returncode == 0:
                            success = True
                            break
                    except Exception:
                        continue

    if success:
        return True

    typer.echo("Warning: Clipboard copy failed.")
    if sys.platform.startswith("linux"):
        typer.echo("To enable clipboard support, please install 'wl-copy', 'xclip', or 'xsel'.")
    elif sys.platform == "darwin":
        typer.echo("Ensure 'pbcopy' is available.")
    
    return False

@typer_app.command(
    name="fix",
    help="Fix typos in the provided TEXT or from stdin.",
    epilog="Commands:\n  config   Configure API key and settings.\n  setup    Interactive configuration wizard."
)
def fix(
    text: Annotated[Optional[List[str]], typer.Argument(help="The text to fix typos in.")] = None,
    suggest: Annotated[bool, typer.Option("--suggest", help="Suggest improvements instead of just fixing.")] = False,
    rewrite: Annotated[bool, typer.Option("--rewrite", help="Rewrite the text completely.")] = False,
):
    mode = "fix"
    if rewrite:
        mode = "rewrite"
    elif suggest:
        mode = "suggest"

    input_text = ""
    if text:
        input_text = " ".join(text)
    
    if not input_text:
        if not sys.stdin.isatty():
            input_text = sys.stdin.read().strip()
        else:
            # wont occur this situation
            typer.echo("No text provided. Please provide text as an argument or via stdin.")
            sys.exit(1)

    # Clean up input and check for empty string
    if not input_text or not input_text.strip():
         typer.echo("Empty text provided.")
         sys.exit(1)

    result = fix_text(input_text, mode=mode)
    
    # Handle config error / missing API key
    if result.startswith("[CONFIG_NEEDED]"):
        friendly_msg = result.replace("[CONFIG_NEEDED] ", "")
        typer.echo(typer.style(friendly_msg, fg=typer.colors.YELLOW, bold=True))
        return

    if result.startswith("Error:"):
        typer.echo(result)
        sys.exit(1)
    
    if mode == "fix":
        typer.echo(result)    
        if copy_to_clipboard(result):
            typer.echo("Copied to clipboard!")
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
                if copy_to_clipboard(selected_text):
                    typer.echo(f"Option {choice} copied to clipboard!")
            else:
                typer.echo("Invalid selection.")
        else:
            # Fallback
            typer.echo("Could not parse options for selection.")

def app():
    known_commands = ["config", "setup"]
    if len(sys.argv) == 1:
        if sys.stdin.isatty():
             sys.argv.insert(1, "fix")
             sys.argv.append("--help")
        else:
             sys.argv.insert(1, "fix")
    else:
        first_arg = sys.argv[1]
        if first_arg not in known_commands:
            sys.argv.insert(1, "fix")
        
    typer_app()

if __name__ == "__main__":
    app()
