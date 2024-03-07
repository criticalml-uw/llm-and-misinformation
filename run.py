import csv
import time
from openai import OpenAI
from os import environ
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

data = pd.read_excel('chat_prompts.xlsx')
data = data.fillna('')

tests = [
    "usmle_1_q",
    "usmle_2_q"
]

test_answers = [
    "usmle_1_a",
    "usmle_2_a"
]

client = OpenAI(api_key=environ.get("OPENAI_API_KEY"))

for item, test in enumerate(tests):
    for idx, row in enumerate(data.itertuples()):
        if idx >= 20:
            break
        with open("results.csv", mode='a', encoding='UTF8') as file:
            writer = csv.writer(file)
            csv_out = []
            csv_out.append(idx)

            prompt = getattr(row, test)

            # Remove multiple choice options, making question open-ended
            prompt = prompt.split("(A)")
            prompt = prompt[0]
            prompt = prompt.replace("which of the following","what")
            prompt = prompt.replace("Which of the following", "What")

            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                  {"role": "system", "content": f"Including an explanation, answer the following question: {prompt}"},
                ],
                max_tokens=2048,
                temperature=0,
            )

            gpt_ans = completion.choices[0].message.content.strip()
            gpt_ans = " ".join(gpt_ans.splitlines())
            data.at[idx, str(test_answers[item])] = gpt_ans
            csv_out.append(gpt_ans)

            writer.writerow(csv_out)
            print(f"Finished question GPT-4's answer: {gpt_ans}")
            print(f"Finished question {idx} for {test}")
            time.sleep(4)

    data.to_excel(f"output_results_{test}.xlsx")
