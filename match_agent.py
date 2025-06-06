import yaml
import os

from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain


def match_agent(match_info, df_list):
    # Set API Key
    # Load the YAML config
    with open("LLM_API_KEY/config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Set the environment variable
    os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

    # Initialize the LLMs models
    creative_llm = ChatOpenAI(temperature=0.7)
    factual_llm = ChatOpenAI(temperature=0)

    # The prompt to generate the match context
    prompt = f"""
        Here is the summary of a football match in JSON format:

        {match_info}

        Write a friendly, informative introduction message that a football chatbot could use to start a conversation with a user about this match.
        Make it engaging and mention the score, the teams, the competition, and the date.
        """

    intro_message = creative_llm.predict(prompt)

    # Initialize the agent
    agent = create_pandas_dataframe_agent(factual_llm, df_list, agent_type="tool-calling", verbose=False, allow_dangerous_code=True)

    return intro_message, agent


def match_chat(match_summary=None, agent=None, user_question=None, memory=None):
    """
    Answers a question about a football match using a dataframe agent and a memory-enhanced LLM.

    Parameters:
    - match_summary : A match summary for memory purpose
    - agent : The dataframe AI agent
    - user_question (str): User's input question.
    - memory (ConversationBufferMemory): Optional existing memory object.

    Returns:
    - str: A friendly, contextualized response from the chatbot.
    - memory: the memory of the discussion for reuse
    """

    # Create LLM
    creative_llm = ChatOpenAI(temperature=0.7)

    # Initialize memory if not provided
    if memory is None:
        memory = ConversationSummaryBufferMemory(llm=creative_llm, max_token_limit=100)
        memory.save_context({"input": "Hello"}, {"output": "What's up"})
        memory.save_context({"input": "Not much, just hanging"},
                            {"output": "Cool"})
        memory.save_context({"input": "What is the summary of the football match that we suppose to talk about ?"},
                            {"output": f"{match_summary}"})

    # Get factual answer from the dataframe agent
    factual_answer = agent.invoke(user_question)
    print(factual_answer)

    # Rephrase with conversation LLM
    prompt = f"""
    You're a football expert chatting casually with a fan. You've just looked at detailed data from the match.

    Here’s what the user asked:
    "{user_question}"

    Here’s what you found in the data:
    "{factual_answer}"

    Now, give a natural, vivid answer. Speak like someone watching the game with friends. 

    Do:
    - Flow naturally from the question to the data.
    - Uses football lingo ("picked up a yellow", "slid in late", "was fired up early", "clean finish", "massive chance", etc).
    - If you have no data keep the response short and brief
    - Explains context in plain terms — like when the card happened, what it meant, or who made the play.
    - Blend data into sentences, don’t list them.
    - If it's a goal, describe it a bit (how, who, what kind of chance — use xG loosely).
    - Say "the xG was around 0.6" instead of quoting exact numbers.
    - Explain the xG simply, like “it was a big chance” or “xG around ...”.
    - If it’s a card, talk about the timing, the player’s reputation, or possible tension.
    - If it’s a sub, foul, injury — explain it like a fan would.
    - Keep it tight — no filler like “hope you enjoyed it” or “just another thrilling moment”.
    - Use normal language like "nice finish", "quick move", "big chance", etc.
    - If no player is mentioned, focus on the play itself.
    - Leaves room for nuance or little commentary ("you could tell the defense was caught out", "a confident finish", etc.)
    - Use real football language: “buried it”, “clean finish”, “latched onto it”, etc.
    - Keep it short, engaging, and grounded — no buzzwords, no hashtags, no emojis.

    Avoid:
    - Sounding robotic or too formal.
    - Do not invent details like xG, cards, or player reactions unless present in the data.
    - Repeating terms like “shot using the right foot” twice.
    - Clichés like “sight to behold”, “thrilling moment”, etc.
    - Avoid any apology or stiff phrases like "Based on the data".
    - Avoids phrases like “it was quite a sight to behold,” “showcasing some real skill,” or robotic patterns.
    - No hashtags. No emojis.

    Speak like someone who loves football and knows how to tell a story.
    """
    conversation = ConversationChain(llm=creative_llm, memory=memory, verbose=False)
    final_response = conversation.predict(input=prompt)

    return final_response, memory
