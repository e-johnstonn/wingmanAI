import os

from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma




class Database:
    def __init__(self, directory):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.directory = directory
        self.files = os.listdir(self.directory)

    def list_files(self):
        if len(self.files) == 0:
            return None
        return self.files

    def save_or_add_to_transcripts(self, name, transcript):
        persist_directory = os.path.join(self.directory, name)
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
        transcript_file = os.path.join(persist_directory, "transcript.txt")
        with open(transcript_file, 'a') as f:
            f.write(transcript + "\n\n")


    def load_db(self, name):
        persist_directory = os.path.join(self.directory, name)
        transcript_file = os.path.join(persist_directory, "transcript.txt")
        with open(transcript_file, 'r') as f:
            transcript = f.read()
        split_docs = self.text_splitter.split_text(transcript)
        db = Chroma.from_texts(texts=split_docs, embedding=self.embeddings)
        return db















