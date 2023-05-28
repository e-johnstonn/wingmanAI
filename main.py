import sys
import queue
import threading
import time

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, \
    QTabWidget, QComboBox, QMessageBox
from PyQt5.QtGui import QFont, QTextCursor

import AudioRecorder
from AudioTranscriber import AudioTranscriber
from chatbot_utils import GPTChat

from vector_utils import *


audio_queue = queue.Queue()

user_audio_recorder = AudioRecorder.DefaultMicRecorder()
user_audio_recorder.record_into_queue(audio_queue)

time.sleep(1)

speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
speaker_audio_recorder.record_into_queue(audio_queue)

global_transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source)
transcribe = threading.Thread(target=global_transcriber.transcribe_audio_queue, args=(audio_queue,))
transcribe.daemon = True
transcribe.start()



class CustomLineEdit(QLineEdit):
    def focusInEvent(self, e):
        super().focusInEvent(e)
        if self.text() == "Send a message...":
            self.clear()

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        if self.text().strip() == "":
            self.setText("Send a message...")


class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Setup")
        self.setStyleSheet("""
            background-color: #424242;
            color: #F5F5F5;
            selection-background-color: #64B5F6;
            font-family: 'Roboto', sans-serif;
        """)
        self.resize(500, 300)

        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { color: black; }")

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "New")
        self.tabs.addTab(self.tab2, "Load")

        self.tab1_layout = QVBoxLayout(self)
        self.tab2_layout = QVBoxLayout(self)

        self.tab1.setLayout(self.tab1_layout)
        self.tab2.setLayout(self.tab2_layout)

        self.welcome_message = QLabel("""
            <h2>Welcome!</h2>
            <h3>Enter the name of the person you will be speaking to and click start.</h3>
        """)

        self.speaker_name_label = QLabel("<h2>Speaker's Name: </h2>")

        self.speaker_name_input = QLineEdit()
        self.speaker_name_input.setStyleSheet("""
            font-size: 14pt;
            color: #F5F5F5;
            background-color: #616161;
            border: none;
            padding: 5px;
        """)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_chat)
        self.start_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                color: #F5F5F5;
                background-color: #616161;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #484848;
            }
        """)

        self.file_dropdown = QComboBox()
        self.file_dropdown.setStyleSheet(self.speaker_name_input.styleSheet())

        self.load_file_button = QPushButton("Load this file")
        self.load_file_button.clicked.connect(self.load_file)
        self.load_file_button.setStyleSheet(self.start_button.styleSheet())

        self.nofiles_label = QLabel()

        self.tab1_layout.addWidget(self.welcome_message)
        self.tab1_layout.addWidget(self.speaker_name_label)
        self.tab1_layout.addWidget(self.speaker_name_input)
        self.tab1_layout.addWidget(self.start_button)

        self.tab2_layout.addWidget(self.file_dropdown)
        self.tab2_layout.addWidget(self.load_file_button)
        self.tab2_layout.addWidget(self.nofiles_label)

        self.layout.addWidget(self.tabs)

        self.db = Database("transcripts_for_vectordb")
        self.load_files_into_dropdown()

    def start_chat(self):
        self.speaker_name = self.speaker_name_input.text()
        if self.speaker_name:
            self.chat_app = ChatApp(self.speaker_name)
            self.chat_app.show()
            self.close()

    def load_file(self):
        selected_file = self.file_dropdown.currentText()
        if selected_file:
            name = str(selected_file)
            loaded_db = self.db.load_db(name)
            self.chat_app = ChatApp(name, loaded_db=loaded_db)
            self.chat_app.show()
            self.close()

    def load_files_into_dropdown(self):
        files = self.db.list_files()

        if files is None:
            self.nofiles_label.setText("No files found!")
            self.nofiles_label.setFont(QFont("Roboto", 16))
            return None
        else:
            self.file_dropdown.addItems(files)






class ChatApp(QWidget):
    def __init__(self, speaker_name, loaded_db=None):
        super().__init__()
        self.create_widgets()
        self.chat = GPTChat()

        self.speaker_name = speaker_name

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_transcript)
        self.timer.start(3000)

        self.response_timer = QTimer()
        self.response_timer.timeout.connect(self.update_placeholder)
        self.placeholder_text = ''

        self.db = loaded_db



    def create_widgets(self):
        self.setWindowTitle("Wingman AI")

        self.setStyleSheet("background-color: #424242;"
                           "color: #F5F5F5;"
                           "selection-background-color: #64B5F6")

        self.resize(800, 600)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabBar::tab { color: black; }")


        #Transcript tab

        transcript_tab = QWidget()

        self.transcript_box = QTextEdit()
        self.transcript_box.setFont(QFont("Roboto", 10))
        self.transcript_box.setReadOnly(True)

        self.recording_label = QLabel()
        self.recording_label.setText("Recording.")

        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_label)
        self.recording_timer.start(1000)

        self.save_quit_button = QPushButton("Save and quit")
        self.save_quit_button.setFont(QFont("Roboto", 12))
        self.save_quit_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                color: #F5F5F5;
                background-color: #616161;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #484848;
            }
        """)
        self.save_quit_button.clicked.connect(self.save_and_quit)

        transcript_layout = QVBoxLayout(transcript_tab)
        transcript_layout.addWidget(self.transcript_box)
        transcript_layout.addWidget(self.recording_label)
        transcript_layout.addWidget(self.save_quit_button)

        self.tab_widget.addTab(transcript_tab, "Transcript")

        #Chat tab

        chat_tab = QWidget()

        self.chat_history_box = QTextEdit()
        self.chat_history_box.setReadOnly(True)
        self.chat_history_box.append("<div style='background-color:#363636  ;padding:10px;margin:5px;border-radius:15px;color:#FFFFFF;font-family:Roboto;font-size:16px;'><b>"
                                     + "Wingman: " + "</b>" + "Hello! I'm Wingman, your personal conversation assistant. I am now monitoring your conversation. How can I help you?" + "</div>")

        self.input_box = CustomLineEdit("Send a message...")
        self.input_box.setFont(QFont("Robotica", 12))
        self.input_box.setStyleSheet("color: darkgray;")
        self.input_box.setMinimumSize(400, 40)


        self.send_button = QPushButton("Send message")
        self.send_button.setFont(QFont("Robotica", 12))
        self.send_button.setStyleSheet("""
            QPushButton {
                font-size: 14pt;
                color: #F5F5F5;
                background-color: #616161;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #484848;
            }
        """)
        self.send_button.clicked.connect(self.on_send)

        self.response_label = QLabel()

        chat_layout = QVBoxLayout(chat_tab)
        chat_layout.addWidget(self.chat_history_box)
        chat_layout.addWidget(self.input_box)
        chat_layout.addWidget(self.send_button)
        chat_layout.addWidget(self.response_label)

        self.tab_widget.addTab(chat_tab, "Chat")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

    @pyqtSlot()
    def update_transcript(self):
        scrollbar = self.transcript_box.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()

        transcript = global_transcriber.get_transcript(speakername=self.speaker_name)
        self.transcript_box.setPlainText(transcript)

        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())

    def update_recording_label(self):
        current_text = self.recording_label.text()
        if len(current_text) < 12:
            current_text += '.'
        else:
            current_text = "Recording."
        self.recording_label.setText(current_text)

    @pyqtSlot()
    def on_send(self):
        user_message = self.input_box.text()
        if user_message:
            self.input_box.clear()
            self.chat_history_box.append(
                "<div style='background-color:#363636   ;padding:10px;margin:5px;border-radius:15px;color:#FFFFFF;font-family:Roboto;font-size:16px;'><b>" + "You: " + "</b>" + user_message + "</div>")
            self.chat_history_box.moveCursor(QTextCursor.End)

            self.placeholder_text = "."
            self.response_timer.start(500)

            threading.Thread(target=self.get_response, args=(user_message,)).start()


    def update_placeholder(self):
        if len(self.placeholder_text) < 3:
            self.placeholder_text += "."
        else:
            self.placeholder_text = "."
        self.response_label.setText("Getting response" + self.placeholder_text)

    def get_response(self, user_message):
        transcript = global_transcriber.get_transcript(speakername=self.speaker_name)

        if self.db:
            context = self.db.similarity_search(user_message, k=2)
            response = self.chat.message_bot(user_message, transcript, context)
        else:
            response = self.chat.message_bot(user_message, transcript)

        self.response_timer.stop()
        self.response_label.clear()
        QApplication.processEvents()
        self.chat_history_box.append("<div style='background-color:#363636  ;padding:10px;margin:5px;border-radius:15px;color:#FFFFFF;font-family:Roboto;font-size:16px;'><b>" + "Wingman: " + "</b>" + response + "</div>")
        self.chat_history_box.update()
        self.chat_history_box.moveCursor(QTextCursor.End)

    def save_transcript(self):
        try:
            speaker_transcript = global_transcriber.get_speaker_transcript()
            db_lock = threading.Lock()
            with db_lock:
                d = Database('transcripts_for_vectordb')
                d.save_or_add_to_transcripts(self.speaker_name, speaker_transcript)
        except Exception as e:
            print(e)

    def save_and_quit(self):
        try:
            self.save_transcript()
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Information)
            msgbox.setText("Transcript saved successfully!")
            msgbox.setWindowTitle("Success")
            msgbox.setStandardButtons(QMessageBox.Ok)
            msgbox.exec_()
            QApplication.quit()

        except Exception as e:
            print(e)




if __name__ == "__main__":
    app = QApplication(sys.argv)

    setup_window = SetupWindow()
    setup_window.show()

    sys.exit(app.exec_())







