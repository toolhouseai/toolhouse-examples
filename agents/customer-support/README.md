# Building a Customer Support Bot with Anthropic and Toolhouse

Hello, developers! Today, we'll walk through creating a customer support bot using Anthropic's AI and Toolhouse's tool management platform. This bot will assist customers with their product-related queries, but only during specific hours.

> 👋 Here's the thing: adding all the super-powers to the chatbot can be achieved with Toolhouse's SDK and just **3 lines of code**.

## Intro video
https://github.com/user-attachments/assets/8ee3af0f-9b03-4fd9-890c-319386b870b3




To build this AI agent for customer support, we're going to be using 3 tools:
- [Get page contents](https://app.toolhouse.ai/store/scraper): This tools lets us get information from the web, about the product we're selling - some amazing headphones
- [Send email](https://app.toolhouse.ai/store/send_email): This tool lets us send the information to a specified email inbox, if the user desires it.
- [Get current time](https://app.toolhouse.ai/store/current_time): This tool returns the time and thus whether the bot should respond to the customer (this is a fun constraint just to showcase this tool)

Let's dive in!

## Background
Our goal is to create an agent that uses LLMs and tools to do this:

- Scrape information from a web source to acquire the knowledge
- Respond to customer queries concisely
- Email information to an email address
- Sleep. Yes, we want the agent to operates only after 6:00 AM PDT. (ℹ️ again, this is just a fun constraint that we're using to showcase how LLMs can reason by using our tools. Feel free to change this value in the system prompt in the agent's code on lines 21-22)

We'll uses Anthropic for natural language processing, and we'll rely on Toolhouse for tool management. This way, we won't have to write the JSON Schema for the tools, and obviously we won't have to build or even run the tool ourselves. We'll use Python for this project, leveraging the `anthropic` and `toolhouse` libraries.

## Setting Up
First, ensure you have the necessary API keys set as environment variables:
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export TOOLHOUSE_API_KEY="your_toolhouse_api_key"
```
## Initializing the Project
Make sure you have installed all dependencies and create your virtual environment as explained in the [main README](https://github.com/toolhouseai/toolhouse-examples/blob/main/README.md) of this repo.

Let's start by importing the required libraries and initializing our clients:

```python
import os
from typing import List
from anthropic import Anthropic
from toolhouse import Toolhouse, Provider

client = Anthropic()
th = Toolhouse(provider=Provider.ANTHROPIC)

# Set timezone for the AI Agent so that it reflects the PT time zone.
th.set_metadata('timezone', '-7')
```

## Defining the System Message
Next, we define the system message that sets the behavior and constraints for our bot, this matters because it gives a purpose to the bot:

```python
# Define system message for the AI agent
system_message = """
        IMPORTANT: Be extremely concise in all your answers. Keep it to 280 characters.
        You are a great customer support agent for a headphones company that is taked to help customers. Answer the question as faithfully as you can.
        You only reply to questions after 6:00AM PDT. 
        You need to find out what the time is. If a question is asked before 6:00AM PDT, you must reply saying: "Sorry, Can't answer right now, please try again later."
        Retrieve knowledge from any source you have and provide the best answer you can.
        Your main source of knowledge is this file which you can access by using a web scraper, but only scrape it once: https://gist.githubusercontent.com/orliesaurus/be34b6b36e79c154c7a3cb625c448ac3/raw/0bbda12501d866eb405263485d099ae4e1b2db76/faqs_headphones.txt
        Only respond with the details of the answer, like a real customer support agent would do.
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

In a moment, you will notice that won't pass a JSON schema when we create our first response. Instead, we pass the `get_tools()` method from the Toolhouse SDK. Toolhouse compiles a JSON schema compatible with Anthropic, complete with prompts and description for the tool and each of its arguments, if present. This matters because you just equipped your LLMs with up to date knowledge, and you gave it the ability to perform actions — all in **just one line of code**.

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

You also noticed that the **tool execution boilerplate is gone.** With Toolhouse, tools are executed in the cloud, and the SDK manages the tool execution and the response handling for you with the `run_tools()` method. Toolhouse is not a framework, so you'll get raw completion objects that you can inspect or further modify if needed. You can also use `run_tools()` if you're running your existing local tools, but we'll leave this for another tutorial.

## Conclusion
With this setup, you have a basic customer support bot that leverages Anthropic's AI capabilities and Toolhouse's tools. This bot will respond to customer queries concisely and only during specified hours. What's best is that you actually saved lines of code because Toolhouse is already handling all the tool related aspects of your code for you.

Feel free to expand this bot's capabilities by adding more sophisticated handling of user inputs and integrating additional tools as needed. Happy coding!
