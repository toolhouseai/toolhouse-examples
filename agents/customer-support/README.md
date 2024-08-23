# Building a Customer Support Bot with Anthropic and Toolhouse

Hello, developers! Today, we'll walk through creating a customer support bot using Anthropic's AI and Toolhouse's tool management platform. This bot will assist customers with their product-related queries, but only during specific hours.

> 👋 Here's the catch: adding all the super-powers to the chatbot can be achieved with Toolhouse's SDK and 3 lines of code.

To build this AI agent for customer support, we're going to be using 3 tools:
- Web scraper: This tools lets us get information from the web, about the product we're selling - some amazing headphones
- Email: This tool lets us send the information to a specified email inbox, if the user desires it.
- Current time: This tool returns the time and thus whether the bot should respond to the customer (it's a fun constraint to showcase this tool)

Let's dive in!

## Background
Our goal is to create a bot that uses LLMs and tools to:

- Scrape information from a web source to acquire the knowledge
- Responds to customer queries concisely.
- Can email information to an address
- Operates only after 6:00 AM PDT. (ℹ️ feel free to change this value in the system prompt in the agent's code on LINE 21-22)
- Uses Anthropic for natural language processing and Toolhouse for tool management

We'll use Python for this project, leveraging the `anthropic` and `toolhouse` libraries.

## Setting Up
First, ensure you have the necessary API keys set as environment variables:
```bash
export ANTHROPIC_KEY="your_anthropic_api_key"
export TOOLHOUSE_BEARER_TOKEN="your_toolhouse_bearer_token"
```
## Initializing the Project
Make sure you have installed all dependencies and create your virtual environment as explained in the [main README](https://github.com/toolhouseai/toolhouse-examples/blob/main/README.md) of this repo.

Let's start by importing the required libraries and initializing our clients:

```python
import os
from typing import List
from anthropic import Anthropic
from toolhouse import Toolhouse, Provider

# Load API keys from environment variables
CLAUDE_API_KEY = os.getenv("ANTHROPIC_KEY")
TH_TOKEN = os.getenv("TOOLHOUSE_BEARER_TOKEN")

# Initialize Anthropic and Toolhouse clients
client = Anthropic(api_key=CLAUDE_API_KEY)
th = Toolhouse(access_token=TH_TOKEN, provider=Provider.ANTHROPIC)

# Set timezone for the AI Agent - to set its hours of operations.
th.set_metadata('timezone', '-7')
```

## Defining the System Message
Next, we define the system message that sets the behavior and constraints for our bot, this matters because it gives a purpose to the bot:

```python
# Define system message for the AI agent
system_message = """
        IMPORTANT: Be extremely concise in all your answers. Keep it to 280 characters.
        You are a great customer support agent for a headphones company that is tasked to help customers. Answer the question as faithfully as you can.
        You only reply to questions after 6:00AM PDT. 
        You need to find out what the time is. If a question is asked before 6:00AM PDT, you must reply saying: "Sorry, Can't answer right now, please try again later."
"""
```

## Processing User Queries
We need a function to handle user queries, we'll implement something that works from the CLI:

```python
first_question = True

def process_response(messages):
    global first_question
    # We add some colors to the input to make it look nice
    input_question = input("\033[36m" + ("Hi I am a customer support bot. What is your question?" if first_question else "Do you have a follow up question?") + " \033[0m")
    first_question = False

    if input_question.lower() in ["/quit", "/exit"]:
        exit()

    messages.append({"role": "user", "content": f"{input_question}"})
```

You will notice that when we create our first response we pass the Toolhouse SDK `get_tools()` method to inform the LLM that there are tools available to achieve its goals. This matters because it's the simplest and most powerful ways to supercharge LLMs with up to date knowledge and give it the option to perform actions.

```python
    response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=system_message,
                # ✨ This is where the magic beings, we call th.get_tools()
                tools=th.get_tools(),
                messages=messages
            )
    # Here the magic continues as we provide the information back to the LLM so it knows how to answer the user            
    messages += th.run_tools(response)
```


## Conclusion
With this setup, you have a basic customer support bot that leverages Anthropic's AI capabilities and Toolhouse's tools. This bot will respond to customer queries concisely and only during specified hours.

Feel free to expand this bot's capabilities by adding more sophisticated handling of user inputs and integrating additional tools as needed. Happy coding!