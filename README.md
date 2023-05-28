# WingmanAI

WingmanAI is a powerful tool for interacting with real-time transcription of both system and microphone audio. Powered by ChatGPT, this tool lets you interact in real-time with the transcripts as an extensive memory base for the bot, providing a unique communication platform. 

## Demo

https://github.com/e-johnstonn/wingmanAI/assets/30129211/ab7d2cdc-8acf-4b80-a41c-fe6adecd6d93
- As you can see, the bot can answer questions about past conversations when you load the transcripts for a designated person. 

## Features

- **Real-time Transcription**: WingmanAI can transcribe both system output and microphone input audio, allowing you to view the live transcription in an easy-to-read format. 

- **ChatGPT Integration**: You can chat with a ChatGPT powered bot that reads your transcripts in real-time.

- **Efficient Memory Management**: The bot maintains a record of the conversation but in a token-efficient manner, as only the current chunk of transcript is passed to the bot. 

- **Save and Load Transcripts**: WingmanAI allows you to save transcripts for future use. You can load them up anytime later, and any query made to the bot will be cross-referenced with a vector database of the saved transcript, providing the bot with a richer context. 

- **Append Conversations**: You can keep appending to the saved transcripts, building a vast database over time for the bot to pull from.




## Installation

1. Clone the repository.
2. Install the requirements: ```pip install -r requirements.txt```
3. If you wish to use CUDA for Whisper (which is highly recommended), uninstall (```pip uninstall torch```) torch and run: ```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117```

**Note**: This application is currently compatible only with Windows. 

## Prerequisites
Ensure you have `ffmpeg` installed on your system.
Have a working OpenAI API key.
Works best using CUDA! CPU transcription is not real-time.
The model currently being used is the "base" model - if your hardware can't run it, change it to "tiny". Language is currently set to English.

## Getting Started
1. Add your OpenAI API key to the `keys.env` file. 
2. Run `main.py`. 


For any queries or issues, feel free to open a new issue in the repository. 

Contributions are always welcomed to improve the project. 

## Acknowledgements

This project uses a modified version of SevaSk's "Ecoute" project for the transcriptions - check it out [here](https://github.com/SevaSk/ecoute)! 



