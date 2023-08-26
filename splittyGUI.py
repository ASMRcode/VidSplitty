import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont
from moviepy.video.io.VideoFileClip import VideoFileClip
import io
import contextlib
import traceback
import requests

# Import the QDarkStyleSheet library
import qdarkstyle

class VideoSplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Splitter")
        self.setGeometry(0, 0, 1080, 900)

        main_layout = QVBoxLayout()

        self.label_path = QLabel("Video Path:")
        self.entry_path = QLineEdit()
        self.button_browse = QPushButton("Browse")
        self.label_duration = QLabel("Clip Duration (seconds):")
        self.entry_duration = QLineEdit()
        self.label_output = QLabel("Output Folder:")
        self.entry_output = QLineEdit()
        self.button_browse_output = QPushButton("Browse")
        self.button_split = QPushButton("Split Video")
        self.console = QTextEdit()

        main_layout.addWidget(self.label_path)
        main_layout.addWidget(self.entry_path)
        main_layout.addWidget(self.button_browse)
        main_layout.addWidget(self.label_duration)
        main_layout.addWidget(self.entry_duration)
        main_layout.addWidget(self.label_output)
        main_layout.addWidget(self.entry_output)
        main_layout.addWidget(self.button_browse_output)
        main_layout.addWidget(self.button_split)
        main_layout.addWidget(self.console)

        # Add a Subscribe Button
        self.button_subscribe = QPushButton("Subscribe to ASMRcode")
        main_layout.addWidget(self.button_subscribe)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.button_browse.clicked.connect(self.browse_file)
        self.button_browse_output.clicked.connect(self.browse_output_folder)
        self.button_split.clicked.connect(self.split_video)
        self.button_subscribe.clicked.connect(self.open_asmrcode)

        self.original_stdout = sys.stdout

        # Apply the dark stylesheet
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()  # Load the stylesheet
        self.setStyleSheet(dark_stylesheet)  # Apply the stylesheet to the application

        # Increase the font size for the buttons
        font = QFont()
        font.setPointSize(12)  # Adjust the font size as needed
        self.button_browse.setFont(font)
        self.button_browse_output.setFont(font)
        self.button_split.setFont(font)
        self.button_subscribe.setFont(font)
        self.label_duration.setFont(font)
        self.label_output.setFont(font)
        self.label_path.setFont(font)
        

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4)", options=options)
        if file_path:
            self.entry_path.setText(file_path)

    def browse_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if output_folder:
            self.entry_output.setText(output_folder)

    def split_video(self):
        video_path = self.entry_path.text()
        clip_duration = int(self.entry_duration.text())
        output_folder = self.entry_output.text()
        os.makedirs(output_folder, exist_ok=True)

        self.log_to_console(f"Splitting video: {video_path}")
        self.log_to_console(f"Clip duration: {clip_duration} seconds")
        self.log_to_console(f"Output folder: {output_folder}")

        try:
            self.redirect_output_to_console()
            self.log_to_console("SPLITTING PLEASE WAIT...")
            split_video(video_path, clip_duration, output_folder)
        except Exception as e:
            self.log_to_console("An error occurred during video splitting:")
            self.log_to_console(str(e))
            traceback.print_exc()
        finally:
            self.restore_output()

        self.log_to_console("Video splitting completed.")

    def open_asmrcode(self):
        import webbrowser
        webbrowser.open("https://www.youtube.com/channel/UC8G3HIV4g4fCmPO7-G5BcnA?sub_confirmation=1")



    def log_to_console(self, text):
        self.console.append(text)

    def redirect_output_to_console(self):
        sys.stdout = EmittingStream(text_written=self.on_text_written)

    def restore_output(self):
        sys.stdout = self.original_stdout

    def on_text_written(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

class EmittingStream(io.TextIOBase):
    def __init__(self, text_written):
        self.text_written = text_written

    def write(self, text):
        if not self.closed and self.text_written:
            self.text_written(text)

def split_video(video_path, clip_duration, output_folder):
    video = VideoFileClip(video_path)
    total_duration = video.duration
    current_time = 0

    base_filename = os.path.splitext(os.path.basename(video_path))[0]  # Get the base filename without extension

    output_folder_with_base = os.path.join(output_folder, base_filename + "_clips")
    os.makedirs(output_folder_with_base, exist_ok=True)

    clip_number = 1

    while current_time + clip_duration <= total_duration:
        start_time = current_time
        end_time = current_time + clip_duration

        clip = video.subclip(start_time, end_time)
        clip_filename = os.path.join(output_folder_with_base, f"clip_{clip_number:02d}.mp4")
        clip.write_videofile(clip_filename, codec="libx264")

        current_time += clip_duration
        clip_number += 1

    # Save the remaining portion as a separate clip
    if current_time < total_duration:
        start_time = current_time
        end_time = total_duration

        remaining_clip = video.subclip(start_time, end_time)
        remaining_clip_filename = os.path.join(output_folder_with_base, f"remaining_clip.mp4")
        remaining_clip.write_videofile(remaining_clip_filename, codec="libx264")

    video.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoSplitterApp()
    window.show()
    sys.exit(app.exec_())
