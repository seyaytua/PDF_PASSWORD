import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import pikepdf

class PasswordCrackerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    status = pyqtSignal(str)

    def __init__(self, pdf_path, password_file):
        super().__init__()
        self.pdf_path = pdf_path
        self.password_file = password_file
        self.is_running = True

    def run(self):
        try:
            with open(self.password_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = f.readlines()
            
            total = len(passwords)
            
            for i, password in enumerate(passwords):
                if not self.is_running:
                    self.status.emit("❌ キャンセルされました")
                    return
                
                password = password.strip()
                
                if i % 10 == 0:
                    self.progress.emit(int((i / total) * 100))
                    self.status.emit(f"🔍 試行中: {password[:20]}...")
                
                try:
                    with pikepdf.open(self.pdf_path, password=password):
                        self.progress.emit(100)
                        self.status.emit(f"✅ パスワード発見！")
                        self.finished.emit(password)
                        return
                except pikepdf.PasswordError:
                    continue
                except Exception as e:
                    continue
            
            self.progress.emit(100)
            self.status.emit("❌ パスワードが見つかりませんでした")
            self.finished.emit("")
            
        except Exception as e:
            self.status.emit(f"❌ エラー: {str(e)}")
            self.finished.emit("")

    def stop(self):
        self.is_running = False

class ModernButton(QPushButton):
    def __init__(self, text, icon_text=""):
        super().__init__()
        self.setText(f"{icon_text} {text}" if icon_text else text)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        self.setFont(QFont("Consolas", 11, QFont.Bold))

class PDFPasswordCrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_path = ""
        self.password_file = ""
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🔓 PDF Password Cracker v2.0")
        self.setGeometry(100, 100, 700, 550)
        self.setStyleSheet(self.get_dark_stylesheet())

        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # ヘッダー
        header = self.create_header()
        layout.addWidget(header)

        # セパレーター
        layout.addWidget(self.create_separator())

        # PDFファイル選択
        pdf_section = self.create_file_section(
            "📄 PDF File",
            "PDFファイルを選択",
            "🔍 Browse",
            self.select_pdf
        )
        layout.addLayout(pdf_section)
        self.pdf_label = pdf_section.itemAt(1).widget()

        # パスワードファイル選択
        password_section = self.create_file_section(
            "🔑 Password List",
            "パスワードリストを選択",
            "🔍 Browse",
            self.select_password_file
        )
        layout.addLayout(password_section)
        self.password_label = password_section.itemAt(1).widget()

        # セパレーター
        layout.addWidget(self.create_separator())

        # プログレスバー
        progress_layout = QVBoxLayout()
        progress_title = QLabel("⚡ Progress")
        progress_title.setFont(QFont("Consolas", 10, QFont.Bold))
        progress_title.setStyleSheet("color: #00ff00;")
        progress_layout.addWidget(progress_title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00ff00;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Consolas';
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:1 #00cc00
                );
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)

        # ステータス表示
        self.status_label = QLabel("💤 待機中...")
        self.status_label.setFont(QFont("Consolas", 10))
        self.status_label.setStyleSheet("""
            color: #00ff00;
            background-color: #1a1a1a;
            padding: 10px;
            border: 1px solid #333333;
            border-radius: 5px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # セパレーター
        layout.addWidget(self.create_separator())

        # ボタン
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_button = ModernButton("Start Cracking", "▶")
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:1 #00cc00
                );
                color: #000000;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff33, stop:1 #00dd00
                );
            }
            QPushButton:pressed {
                background: #009900;
            }
        """)
        self.start_button.clicked.connect(self.start_cracking)

        self.stop_button = ModernButton("Stop", "⏹")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3333;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        self.stop_button.clicked.connect(self.stop_cracking)
        self.stop_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        # スペーサー
        layout.addStretch()

        # フッター
        footer = QLabel("Made with 💚 by Programmer")
        footer.setFont(QFont("Consolas", 9))
        footer.setStyleSheet("color: #666666;")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        main_widget.setLayout(layout)

    def create_header(self):
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        title = QLabel("🔓 PDF PASSWORD CRACKER")
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        title.setStyleSheet("""
            color: #00ff00;
            background-color: #0d0d0d;
            padding: 15px;
            border: 2px solid #00ff00;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("v2.0 - Hacker Edition")
        subtitle.setFont(QFont("Consolas", 9))
        subtitle.setStyleSheet("color: #00cc00;")
        subtitle.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_widget.setLayout(header_layout)
        
        return header_widget

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #333333;")
        return line

    def create_file_section(self, title, placeholder, button_text, callback):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # タイトル
        title_label = QLabel(title)
        title_label.setFont(QFont("Consolas", 10, QFont.Bold))
        title_label.setStyleSheet("color: #00ff00;")

        # ファイルパス表示
        file_label = QLabel(placeholder)
        file_label.setFont(QFont("Consolas", 9))
        file_label.setStyleSheet("""
            color: #999999;
            background-color: #1a1a1a;
            padding: 10px;
            border: 1px solid #333333;
            border-radius: 5px;
        """)
        file_label.setWordWrap(True)

        # ボタン
        button = ModernButton(button_text)
        button.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 2px solid #00ff33;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        button.clicked.connect(callback)

        layout.addWidget(title_label)
        layout.addWidget(file_label)
        layout.addWidget(button)

        return layout

    def get_dark_stylesheet(self):
        return """
            QMainWindow {
                background-color: #0d0d0d;
            }
            QWidget {
                background-color: #0d0d0d;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QLabel {
                color: #00ff00;
            }
            QMessageBox {
                background-color: #1a1a1a;
                color: #00ff00;
            }
            QMessageBox QLabel {
                color: #00ff00;
            }
            QMessageBox QPushButton {
                background-color: #2a2a2a;
                color: #00ff00;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3a3a3a;
            }
        """

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDFファイルを選択", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.pdf_path = file_path
            self.pdf_label.setText(f"✅ {Path(file_path).name}")
            self.pdf_label.setStyleSheet("""
                color: #00ff00;
                background-color: #1a1a1a;
                padding: 10px;
                border: 1px solid #00ff00;
                border-radius: 5px;
            """)

    def select_password_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "パスワードリストを選択", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.password_file = file_path
            self.password_label.setText(f"✅ {Path(file_path).name}")
            self.password_label.setStyleSheet("""
                color: #00ff00;
                background-color: #1a1a1a;
                padding: 10px;
                border: 1px solid #00ff00;
                border-radius: 5px;
            """)

    def start_cracking(self):
        if not self.pdf_path:
            self.show_message("エラー", "PDFファイルを選択してください", "error")
            return
        
        if not self.password_file:
            self.show_message("エラー", "パスワードリストを選択してください", "error")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🚀 解析開始...")

        self.worker = PasswordCrackerThread(self.pdf_path, self.password_file)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.cracking_finished)
        self.worker.start()

    def stop_cracking(self):
        if self.worker:
            self.worker.stop()
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.status_label.setText("⏹ 停止しました")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def cracking_finished(self, password):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        if password:
            self.show_message(
                "成功！",
                f"パスワードが見つかりました！\n\n🔑 パスワード: {password}",
                "success"
            )
        else:
            self.show_message(
                "失敗",
                "パスワードが見つかりませんでした。\n別のパスワードリストを試してください。",
                "error"
            )

    def show_message(self, title, message, msg_type):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == "success":
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Warning)
        
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # ダークパレット設定
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(13, 13, 13))
    palette.setColor(QPalette.WindowText, QColor(0, 255, 0))
    palette.setColor(QPalette.Base, QColor(26, 26, 26))
    palette.setColor(QPalette.AlternateBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 255, 0))
    palette.setColor(QPalette.ToolTipText, QColor(0, 255, 0))
    palette.setColor(QPalette.Text, QColor(0, 255, 0))
    palette.setColor(QPalette.Button, QColor(42, 42, 42))
    palette.setColor(QPalette.ButtonText, QColor(0, 255, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(0, 204, 0))
    palette.setColor(QPalette.Highlight, QColor(0, 255, 0))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = PDFPasswordCrackerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()