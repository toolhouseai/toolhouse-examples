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

# Set timezone for the AI Agent
th.set_metadata('timezone', '-7')

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

# Initialize message history
messages: List = []
# Flag to check if it's the first question
first_question = True

def process_response(messages):
    global first_question
    
    # Prompt user for question (different for first and follow-up questions)
    if first_question:
        input_question = input("\033[36mHi I am a customer support bot. What is your question? \033[0m")
        first_question = False
    else:
        input_question = input("\033[36mDo you have a follow up question? \033[0m")
    
    # Exit if user types '/quit' '/exit'
    if input_question.lower() in ["/quit", "/exit"]:
        exit()

    
    # Add user's question to message history
    messages.append({"role": "user", "content": f"{input_question}" })
    
    # Generate initial response using Anthropic model
    response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=system_message,
                # Get the tools from toolhouse SDK to perform actions based on the request
                tools=th.get_tools(),
                messages=messages
            )
    
    # Run tools based on the response
    messages += th.run_tools(response)
    
    # Generate final response
    agent_setup = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    system=system_message,
    tools=th.get_tools(),
    messages=messages
    )
    agent_reply = agent_setup.content[0].text
    
    # Print AI agent's response
    print("\033[33mSupport AI AGENT:\033[0m", agent_setup.content[0].text)
    
    # Add AI's response to message history
    messages.append({"role": "assistant", "content": f"{agent_reply}" })

# Main loop to continuously process responses
while True:
    process_response(messages)