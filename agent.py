import os
import sys
import subprocess
import json
import getpass
import textwrap
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

# Initialize rich console for better terminal output
console = Console()

def setup_api():
    """Set up the Gemini API key from environment or prompt user."""
    load_dotenv()  # Try to load from .env file
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        console.print(Panel("[yellow]Gemini API key not found in environment[/yellow]"))
        api_key = getpass.getpass("Enter your Gemini API key: ")
        
        # Save to .env file for future use
        with open(".env", "a") as f:
            f.write(f"\nGEMINI_API_KEY={api_key}")
        
        console.print("[green]API key saved to .env file for future use[/green]")
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def get_plan(model, task):
    """Generate a plan of action using Gemini AI."""
    prompt = f"""
    You are an AI task agent running on a local computer. You need to help the user perform this task: 
    
    "{task}"
    
    Generate a step-by-step plan with specific commands to execute on their local system.
    Your response should be in the following JSON format:
    {{
      "plan_description": "Brief description of your approach",
      "steps": [
        {{
          "description": "What this step does",
          "command": "actual bash command to run",
          "is_command": true
        }},
        {{
          "description": "Code generation explanation",
          "code": "code content here with proper indentation",
          "filename": "example.py",
          "is_command": false
        }}
      ]
    }}
    
    Rules:
    1. For code generation, include proper filenames and complete code (not snippets).
    2. For commands, use standard bash/terminal commands that work cross-platform when possible.
    3. If you need multiple commands in sequence, create separate steps.
    4. Include error handling and validation steps where appropriate.
    """
    
    response = model.generate_content(prompt)
    try:
        response_text = response.text
        # Extract JSON content if it's within markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
            
        plan = json.loads(response_text)
        return plan
    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing AI response: {e}[/red]")
        console.print(Panel(response.text, title="Raw AI Response"))
        return None

def display_plan(plan):
    """Format and display the execution plan to the user."""
    console.print(Panel(f"[bold blue]Task Plan: [/bold blue]{plan['plan_description']}"))
    
    for i, step in enumerate(plan["steps"], 1):
        console.print(f"\n[bold]Step {i}:[/bold] {step['description']}")
        
        if step.get("is_command", False):
            console.print(Panel(step["command"], title="Command to Execute"))
        elif "code" in step:
            console.print(Panel(step["code"], title=f"Code to Save in {step.get('filename', 'file')}"))

def execute_plan(plan):
    """Execute the plan step by step."""
    for i, step in enumerate(plan["steps"], 1):
        console.print(f"\n[bold yellow]Executing Step {i}:[/bold yellow] {step['description']}")
        
        try:
            if step.get("is_command", False):
                console.print(Panel(step["command"], title="Executing Command"))
                result = subprocess.run(
                    step["command"], 
                    shell=True, 
                    text=True, 
                    capture_output=True
                )
                
                if result.returncode == 0:
                    if result.stdout.strip():
                        console.print(Panel(result.stdout, title="Command Output"))
                    console.print("[green]✓ Command executed successfully[/green]")
                else:
                    console.print(Panel(result.stderr, title="[red]Command Error[/red]"))
                    console.print("[red]✗ Command failed[/red]")
                    return False, f"Command failed: {result.stderr}"
                    
            elif "code" in step:
                filename = step.get("filename", "output.py")
                console.print(f"Creating file: [cyan]{filename}[/cyan]")
                
                with open(filename, "w") as f:
                    f.write(step["code"])
                console.print(f"[green]✓ File created successfully[/green]")
                
        except Exception as e:
            console.print(f"[red]✗ Error executing step {i}: {str(e)}[/red]")
            return False, str(e)
            
    return True, "All steps completed successfully"

def refine_plan(model, task, error_details):
    """Get a refined plan based on the error."""
    prompt = f"""
    You are an AI task agent. The previous plan for this task failed:
    
    Original task: "{task}"
    
    Error details: {error_details}
    
    Please generate a refined plan that addresses this error. Your response should be in the following JSON format:
    {{
      "plan_description": "Brief description of your revised approach",
      "steps": [
        {{
          "description": "What this step does",
          "command": "actual bash command to run",
          "is_command": true
        }},
        {{
          "description": "Code generation explanation",
          "code": "code content here with proper indentation",
          "filename": "example.py",
          "is_command": false
        }}
      ]
    }}
    
    Make sure to fix the specific issue that caused the failure.
    """
    
    response = model.generate_content(prompt)
    try:
        response_text = response.text
        # Extract JSON content if it's within markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
            
        plan = json.loads(response_text)
        return plan
    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing AI response for refinement: {e}[/red]")
        console.print(Panel(response.text, title="Raw AI Response"))
        return None

def main():
    console.print(Panel("[bold]Local AI Task Agent[/bold]\nUse AI to automate tasks on your computer", 
                     style="blue"))
    
    # Initialize the AI model
    try:
        model = setup_api()
    except Exception as e:
        console.print(f"[red]Failed to initialize AI: {str(e)}[/red]")
        return
    
    # Get the task
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = console.input("[bold yellow]Enter the task you want to perform:[/bold yellow] ")
    
    # Loop until task is successful or user quits
    while True:
        # Generate plan using AI
        console.print("\n[bold]Generating plan using Gemini AI...[/bold]")
        plan = get_plan(model, task)
        
        if not plan:
            console.print("[red]Failed to generate a valid plan. Please try again.[/red]")
            break
        
        # Display plan and ask for confirmation
        display_plan(plan)
        
        if not Confirm.ask("\nDo you approve this plan?"):
            console.print("[yellow]Plan rejected. Exiting.[/yellow]")
            break
        
        # Execute the plan
        console.print("\n[bold]Executing plan...[/bold]")
        success, message = execute_plan(plan)
        
        if success:
            console.print("\n[bold green]✅ Task completed![/bold green]")
            if Confirm.ask("Was the task successful?"):
                console.print("[green]Great! Task completed successfully.[/green]")
                break
            else:
                # Get feedback for refinement
                error_details = console.input("[yellow]Please describe what went wrong:[/yellow] ")
                console.print("\n[bold]Refining the plan based on feedback...[/bold]")
                plan = refine_plan(model, task, error_details)
                if not plan:
                    console.print("[red]Failed to refine the plan. Please try again.[/red]")
                    break
        else:
            console.print(f"\n[bold red]❌ Task failed:[/bold red] {message}")
            console.print("\n[bold]Refining the plan based on error...[/bold]")
            plan = refine_plan(model, task, message)
            if not plan:
                console.print("[red]Failed to refine the plan. Please try again.[/red]")
                break

if __name__ == "__main__":
    main()