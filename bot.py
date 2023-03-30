# bot.py
import os
import openai
import random
import discord
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
openai.api_key = os.getenv('OPEN_AI_KEY')

model = "gpt-3.5-turbo"
# model = "davinci"

prompt = """
Please generate ten trivia questions, where the answer is the name of a country. The format should be JSON, such as:

[
{
  "question": "What country is home to the world's largest coral reef system?",
  "answer": "Australia"
},
{
  "question": "What country has a capital of Ulaanbaatar",
  "answer": "Mongolia"
},
... (10 more) ...
]

Please use any country, and ask a single fact about the country, where the answer is the name of the country.

Please leave off any explanation - and only provide the JSON as if you're giving an API response.
"""


def more_questions():
    # Generate a response
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    response = completion.choices[0].message.content
    try:
        response = json.loads(response)
        return response
    except KeyError:
        return []


try:
    question_database = json.load(open('questions.json', 'r'))
    print(f"Loaded {len(question_database)} questions")
except FileNotFoundError:
    print("Generating questions...")
    question_database = more_questions()
    json.dump(question_database, open('questions.json', 'w'))


def append_questions():
    global question_database
    question_database += more_questions()


last_questions = {}


def answers_equal(given_answer, answer):
    given_answer = given_answer.lower()
    answer = answer.lower()
    given_answer = "_".join(given_answer.split(' '))
    answer = "_".join(answer.split(' '))
    return given_answer == answer


@client.event
async def on_message(message):
    global last_questions
    print(f"Asked - {message.content}")
    if client.user in message.mentions:
        print(f"Asked - {message.content}")
        if message.content.rstrip().endswith('question'):
            print("Asking questions...")
            question = random.choice(question_database)
            last_questions[message.channel.id] = question
            print(f"Answer is {question['answer']}")
            await message.channel.send(question['question'])
        elif message.content.rstrip().endswith('!generate'):
            print("Generating new questions...")
            append_questions()
            json.dump(question_database, open('questions.json', 'w'))
            await message.channel.send(f"Loaded {len(question_database)} questions available")
        else:
            try:
                given_answer = message.content.split('>')[1].strip()
                actual_answer = last_questions[message.channel.id]['answer']
            except KeyError:
                await message.channel.send('No question!')
                return

            if answers_equal(given_answer, actual_answer):
                await message.channel.send('Correct!')
                del last_questions[message.channel.id]
            else:
                await message.channel.send('Incorrect!')
            print(f"Answered - {message.content}")


client.run(TOKEN)
