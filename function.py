from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="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")
# Make a chat completion request
completion = client.chat.completions.create(
    model="gpt-4o-mini",  # Use GPT-40-mini
    messages=[
        {"role": "user", "content": "How to install matplotlib?"}
    ],
    stream=False  # Set to True if you want streaming responses
)

# Print the response
print(completion.choices[0].message["content"])
