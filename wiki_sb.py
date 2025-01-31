import openai


with open("wiki_sbp.txt", "r") as file:
    data = file.read()


def return_prompt_sb(text, lang="en"):
    return f"""{data}
--
Text: {text}

Category:"""


if __name__ == "__main__":

    openai.api_key = "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"
    a = (
        "your favorite neighborhood got nick how you guys doing "
        + "today welcome to a brand "
        + "new video well actually guys who am i kidding gotnicks don't look"
        + " like this gupnicks don't have macbooks either PROFANITY_TOKEN my setup is"
        + " falling apart in this video by the way guys that was just a subtle flex "
        + "i'm actually gonna release a video on my second channel about um "
        + "the macbook experience i recently switched"
    )
    response = openai.Completion.create(
        engine="code-davinci-002",
        prompt=return_prompt_sb(a),
        temperature=0.5,
        max_tokens=40,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["--"],
    )

    print(response.choices[0].text)
