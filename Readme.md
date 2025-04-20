# AI Task Agent

An intelligent agent that uses AI to help you perform tasks on your local computer through the command line.

## Features

- 🤖 Uses Gemini AI to generate task execution plans
- 📋 Shows you the plan before running anything
- 🖥️ Executes commands and creates files on your system
- 🔄 Automatically refines solutions if they don't work
- 🔒 Safely stores your API key for future use

## Installation

1. Clone this repository:
```
git clone https://github.com/Aakash6545/python-ai-agent.git
cd ai-task-agent
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install google-generativeai python-dotenv rich
```

## Getting Started

1. Get a Gemini API key:
   - Go to https://ai.google.dev/
   - Sign up for a Google AI Studio account
   - Create an API key

2. Run the agent:
```
python agent.py "Your task description here"
```

The first time you run it, the agent will ask for your API key and save it for future use.

## How It Works

1. You describe a task you want to perform
2. The agent uses AI to create a step-by-step plan
3. You review and approve the plan
4. The agent executes each step (running commands, creating files)
5. You confirm if the task was successful
6. If not, the agent learns from your feedback and tries again

## Example Usage

```
python agent.py "Create a simple Python web server and test it"
```

## Requirements

- Python 3.6+
- Internet connection (for Gemini API)
- Gemini API key

## Limitations

- Only uses free Gemini API
- Limited to command-line operations
- Does not remember past tasks between sessions

## Future Improvements

- VSCode extension support
- Learning from past successful solutions
- Support for other AI providers
- Enhanced safety features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
