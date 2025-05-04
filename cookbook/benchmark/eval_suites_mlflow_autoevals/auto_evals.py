from dotenv import load_dotenv

load_dotenv()

import mishikallm

from autoevals.llm import *

###################

# mishikallm completion call
question = "which country has the highest population"
response = mishikallm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": question}],
)
print(response)
# use the auto eval Factuality() evaluator

print("calling evaluator")
evaluator = Factuality()
result = evaluator(
    output=response.choices[0]["message"][
        "content"
    ],  # response from mishikallm.completion()
    expected="India",  # expected output
    input=question,  # question passed to mishikallm.completion
)

print(result)
