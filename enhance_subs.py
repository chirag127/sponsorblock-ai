"""
This module contains the function that corrects the transcription.
"""

import json
import random
from time import sleep

import cohere

from reques import post_url

api_keys = [
    "VH8ou2T7cDKdPfNXCHV4UuJ30wLu7AEOUWt0seHf",
    "ub0uGukJWbvcD5xSm60nf6NOph5KaDnlT8mQbEoW",
    "icuEwMea6R749J6OVMaAvfvt048qJtkAGrf0Vhid",
    "gXAHD12NW6mPdZ9uM83bjXsiK7XexqK42zsdJnEe",
    "NURb2ALICTPc0rrG5nyPnsrTqszFb5TeO8zxqeoI",
    "zvO6WgNxg8Db9S5RbZ9fsZWb2Kn7AfjgXHo6NVAV",
]


def return_prompt(transcription, translation="Na"):
    return f"""This is voice-to-text transcription corrector.
And also translate the trancription if it is in hindi.

Given a transcribed excerpt with errors,
the model responds with the correct version of the excerpt.

Incorrect transcription: I am balling into hay to read port missing credit card.
I lost by card when I what's at the grocery store and I need to see sent a new one.

Google translate: Na

Correct transcription: I am calling in today to report a missing credit card.
I lost my card when I was at the grocery store and I need to be sent a new one.
--
Incorrect transcription: please love,subscription and share

Google translate: Na

Correct transcription: please like, subscribe and share
--
Incorrect transcription: पूरा नाम बोला जा रहा है दामोदर दास दामोदर दास

Google translate: The full name is being said Damodar Das Damodar Das

Correct transcription: Full name is being spoken, Damodar Das Damodar Das
--
Incorrect transcription: क्या बोला हूं आपको मैं कंफ्यूज दूंगा मुझे भैया चेन्नई जी भाई

Google translate: What have I told you
I will confuse me brother Chennai ji brother

Correct transcription: What should I call you?
I am confused You can call me "bhaiya", "Channi ji", "bhai".
--
Incorrect transcription: यह रेलवे कॉलोनी नहीं है?, रेलवे कॉलोनी में हॉस्पिटल के पीछे,
क्या कर रही है

Google translate: This is not a railway colony?, Behind the hospital in railway colony,
what are you doing

Correct transcription: This is not railway colony? railway colony is behind the hospital,
what are you doing here?
--
Incorrect transcription: how are your

Google translate: Na

Correct transcription: how are you?
--
Incorrect transcription: मई आपको ऐसे ही एक बच्चे के बारे में बताना चाहूंगी,

Google translate: May I want to tell you about one such child

Correct transcription: I'd like to tell you about one such child,
--
Incorrect transcription: हो सकता है कि आप चाहते हों कि आप का नऋर्नमेनटेन्ड ह्यबिना किसी समर्थन के हृ विशेष स्कूल , या किसी स्...

Google translate: It is possible that you want your new name to be a special school without any support, or any...

Correct transcription: You may want your child to go to a school that is not run by the LEA - a non-maintained special scho...
--
Incorrect transcription: हाल में नेपाल के हस्पताल सामन्यतया आयुर्वेद, प्राकृतिक चिकित्सा तथा आधुनिक चिकीत्सा करके सरकारी सेवा...

Google translate: Recently, hospitals in Nepal generally serve the government by doing Ayurveda, Naturopathy and Modern Medicine.

Correct transcription: And now at present the naturecure, Ayurvedic and modern treatments are taking place through the gove...
--
Incorrect transcription: I got got charged interest on ly credit card but I paid my pull balance one day due date. I not missed a pavement year yet. Man you reverse the interest charge?

Google translate: Na

Correct transcription: I was charged interest on my credit card but I paid my full balance one day before the due date. I have not missed a payment year yet. Can you reverse the interest charge?
--
Incorrect transcription: क्या हो गया कुछ अटक गया

Google translate: what happened something got stuck

Correct transcription: what happened? something got stuck?
--
Incorrect transcription: ऑटो वालों की साइकिल चलाएंगे क्या

Google translate: Will the auto drivers run the cycle?

Correct transcription:  autos have a strike today.
----
Incorrect transcription: अब आप बहुत से बहुत धन्यवाद देते हों हैं

Google translate: now thank you very much

Correct transcription: now you say a lot of thanks
--
Incorrect transcription: Can you repeat the dates for the three and five dear fixed mortgages? I want to compare them a gain the dates I was quoted by a other broker.

Google translate: Na

Correct transcription: Can you repeat the rates for the three and five year fixed mortgages? I want to compare them against the rates I was quoted by another broker.
--
Incorrect transcription: these indo is sponsor by the government of India and the government of the United States of America.

Google translate: Na

Correct transcription: This video is sponsored by the government of India and the government of the United States of America.
--
Incorrect transcription: अब घंटे की धुन पर

Google translate: now  on the hour of the clock

Correct transcription: now on the tune of the bell
--
Incorrect transcription: कोई नाम भी है सब छोकरी बुलाते हैं मैं मीनू रातों की नींद छीन हूं

Google translate: There is also a name, everyone calls me, I am taking the night's sleep

Correct transcription: I have many names too, everyone calls me meenu, I steal the sleep of the nights.
--
Incorrect transcription: मैं किसी को कुछ नहीं रहा हूं

Google translate: I'm nobody

Correct transcription: I am not telling anybody anything
--
Incorrect transcription: क्या आप मुझे बता सकते हैं कि यह किस कार का है?

Google translate: Incorrect transcription: Can you tell me what car it is?

Correct transcription: Can you tell me what type it is?
--
Incorrect transcription: {transcription}

Google translate: {translation}

Correct transcription:"""


def return_corrected_transcription(
    transcription, translation="Na", prompt_function=return_prompt
):
    """
    It takes in a transcription, and returns a corrected transcription

    :param transcription: The transcription that you want to correct
    :return: The corrected transcription.
    """
    api_key = random.choice(api_keys)

    transcription_length = len(transcription)

    approx_token_count = transcription_length // 3

    cohere_client = cohere.Client(api_key)
    try:
        # models are xlarge,large,medium,small,xsmall
        response = cohere_client.generate(
            model="xlarge-20221108",
            prompt=prompt_function(transcription, translation),
            max_tokens=max(approx_token_count, 40),
            temperature=0.6,
            k=0,
            p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop_sequences=["--", "Incorrect transcription:", "\n"],
            return_likelihoods="NONE",
        )
    except Exception as error:  # pylint: disable=broad-except
        print(error)
        sleep(60)

        return return_corrected_transcription(transcription, translation)

    correct_transcription = response.generations[0].text

    # print(correct_transcription)

    if correct_transcription.endswith("--"):

        correct_transcription = correct_transcription[:-2]

    if "Incorrect transcription:" in correct_transcription:

        # then the correct transcription is the part before the Incorrect transcription

        correct_transcription = correct_transcription.split("Incorrect transcription:")[
            0
        ]

    correct_transcription = correct_transcription.strip()

    print(f"""Incorrect transcription: {transcription}

Google translate: {translation}

Correct transcription: {correct_transcription}""")
    return correct_transcription


def return_corrected_transcription_from_playgroud(transcription):
    """
    It takes in a transcription, and returns a corrected transcription

    :param transcription: The transcription that you want to correct
    :return: The corrected transcription.
    """

    headers = {
        "authority": "production.api.os.cohere.ai",
        "method": "POST",
        "path": "/playground/xlarge/generate",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTkxODkzNTgsImlhdCI6MTY2NzY1MzM1OCwidXNlcl9pZCI6ImQ0MzJlNTk3LTY4YmEtNDFhMy05MDFkLTVhN2ViZTRkZjQ2MCJ9.jE1aqV7wnFaBSrzHpXeXNQD4Ffa6HEuAcCgSHtXXw1g",
        "content-length": "1193",
        "content-type": "text/plain;charset=UTF-8",
        "dnt": "1",
        "origin": "https://os.cohere.ai",
        "referer": "https://os.cohere.ai/",
        "request-source": "playground",
        "sec-ch-ua": '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26",
    }

    transcription_length = len(transcription)

    approx_token_count = transcription_length // 3

    data = {
        "prompt": return_prompt(transcription),
        "max_tokens": max(40, approx_token_count),
        "temperature": 0.7,
        "k": 0,
        "p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop_sequences": ["--", "\n"],
        "prompt_vars": {},
        "language": "en",
    }

    response = post_url(
        "https://production.api.os.cohere.ai/playground/xlarge/generate",
        headers=headers,
        data=json.dumps(data),
    )

    corrected_transcription = response.text

    print(corrected_transcription)

    if corrected_transcription.endswith("--"):
        corrected_transcription = corrected_transcription[:-2]

    corrected_transcription = corrected_transcription.strip()

    print(f"""Incorrect transcription: {transcription}

Correct transcription: {corrected_transcription}""")

    return corrected_transcription


if __name__ == "__main__":
    # return_corrected_transcription("I going bill  because you killed my brother")

    return_corrected_transcription(
        "याद रहेगा तो मैं भी चलता हूं कभी सपनों में मिलता हूं",
        "If you remember, I also walk, sometimes I meet in dreams",
    )
    return_corrected_transcription("this is why I am not doing the beal")
