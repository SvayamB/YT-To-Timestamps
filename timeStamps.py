import os
from youtube_transcript_api import YouTubeTranscriptApi
import re
import google.generativeai as genai
import streamlit as st
from pytube import YouTube
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

def is_valid_input(input_string):
    pattern = r"\[[^\[\]]+\]\s*-\s*\[\d+:\d+\]"
    return bool(re.match(pattern, input_string))
def process_text(input_url):
    yt = YouTube(input_url)
    url_id = yt.video_id
    arrDicts = YouTubeTranscriptApi.get_transcript(url_id)
    totText = ""
    for x in range(len(arrDicts)):
        currDict = arrDicts[x]
        currDict.pop("duration")
        new_dict = {"start": currDict["start"], "text": currDict["text"]}
        arrDicts[x] = new_dict
    for entry in arrDicts:
        minutes = int(entry['start']) // 60
        seconds = int(entry['start']) % 60
        entry['start'] = f"{minutes}:{seconds:02d}"
        totText += (entry['start'] + " " + entry['text'] + "\n")  # Format seconds to have leading zero if necessary

    # pyperclip.copy(totText)
    # print(len(totText))
    x=0
    while(x<10):
        model = genai.GenerativeModel('gemini-pro')
        totText = totText + "]\n group this into chapters with timestamps\n"
        totText = totText + "Format should be [CHAPTER NAME 1]- [Start time 1], [CHAPTER NAME 2]- [Start time 2]"
        response = model.generate_content(totText)
        if(is_valid_input(response.text)):
            text = response.text + "\n"
            text += "Please add a new line after each chapter,keep the times"
            response = model.generate_content(text)
            return response.text
        x+=1
    return x

# Title of the app
st.title('YouTube Video ID Processor')

# Add a text input widget
input_url = st.text_input('Enter a YouTube video URL')

# Process the URL when the user clicks the button
if st.button('Process URL'):
    if input_url:
        # Validate the URL and extract video ID
        try:
            output = process_text(input_url)
            print(output)
            st.write('Here are the Timestamps:')
            st.write(output)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning('Please enter a YouTube video URL to process')

# input='https://www.youtube.com/watch?v=lSAFVMaaH-w&ab_channel=ApesinCapes'#sys.argv[1]
# print(process_text())
