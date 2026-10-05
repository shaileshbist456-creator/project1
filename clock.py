import os
import sys
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QTime, QTimer, QUrl
from PySide6.QtGui import QBrush, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)


class ClockApp(QWidget):

    def __init__(self):
        super().__init__()

        # =========================
        # WINDOW SETUP
        # =========================
        self.setWindowTitle("My Clock")
        self.resize(850, 650)
        self.setWindowIcon(self.create_clock_icon())

        # =========================
        # STATE VARIABLES
        # =========================
        self.stopwatch_seconds = 0
        self.stopwatch_running = False

        self.timer_seconds = 0
        self.timer_running = False

        self.alarms = []
        self.alarm_sound = None

        # =========================
        # AUDIO PLAYER
        # =========================
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.8)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        # =========================
        # UI & TIMER INITIALIZATION
        # =========================
        self.create_ui()

        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.update_everything)
        self.main_timer.start(1000)

    # ==========================================================
    # ICON CREATION
    # ==========================================================
    def create_clock_icon(self):
        pixmap = QPixmap(256, 256)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Clock outer circle
        painter.setPen(QPen(Qt.white, 12))
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(25, 25, 206, 206)

        # Clock hands
        painter.setPen(QPen(Qt.white, 10))

        # Hour hand
        painter.drawLine(128, 128, 128, 75)

        # Minute hand
        painter.drawLine(128, 128, 175, 128)

        # Center dot
        painter.setBrush(QBrush(Qt.white))
        painter.drawEllipse(120, 120, 16, 16)

        painter.end()
        return QIcon(pixmap)

    # ==========================================================
    # MAIN UI & STYLING
    # ==========================================================
    def create_ui(self):
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.create_clock_tab()
        self.create_stopwatch_tab()
        self.create_timer_tab()
        self.create_alarm_tab()

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # Styling
        self.setStyleSheet("""
        QWidget {
            background-color: #0d1117;
            color: white;
            font-family: Arial;
        }

        QTabWidget::pane {
            border: 1px solid #30363d;
            border-radius: 10px;
        }

        QTabBar::tab {
            background-color: #161b22;
            color: #aaaaaa;
            padding: 14px 25px;
            margin-right: 2px;
            border-radius: 8px;
            font-size: 14px;
        }

        QTabBar::tab:selected {
            background-color: #238636;
            color: white;
        }

        QPushButton {
            background-color: #21262d;
            color: white;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px 18px;
            font-size: 15px;
        }

        QPushButton:hover {
            background-color: #30363d;
        }

        QPushButton:pressed {
            background-color: #238636;
        }

        QSpinBox {
            background-color: #161b22;
            color: white;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 10px;
            font-size: 17px;
        }

        QTimeEdit {
            background-color: #161b22;
            color: white;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 10px;
            font-size: 20px;
        }

        QListWidget {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 8px;
            font-size: 16px;
        }

        QListWidget::item {
            padding: 12px;
            border-bottom: 1px solid #30363d;
        }

        QListWidget::item:selected {
            background-color: #238636;
        }

        QSlider::groove:horizontal {
            height: 6px;
            background: #30363d;
            border-radius: 3px;
        }

        QSlider::handle:horizontal {
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
            background: #238636;
        }
        """)

    # ==========================================================
    # CLOCK TAB
    # ==========================================================
    def create_clock_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        title = QLabel("CURRENT TIME")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22))

        self.clock_label = QLabel("--:--:--")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setFont(QFont("Arial", 70, QFont.Bold))

        self.date_label = QLabel("")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setFont(QFont("Arial", 22))

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.clock_label)
        layout.addWidget(self.date_label)
        layout.addStretch()

        self.tabs.addTab(tab, "🕐 Clock")

    # ==========================================================
    # STOPWATCH TAB
    # ==========================================================
    def create_stopwatch_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        title = QLabel("STOPWATCH")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22))

        self.stopwatch_label = QLabel("00:00:00")
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setFont(QFont("Arial", 70, QFont.Bold))

        start_button = QPushButton("▶ START")
        pause_button = QPushButton("⏸ PAUSE")
        reset_button = QPushButton("↻ RESET")

        start_button.clicked.connect(self.start_stopwatch)
        pause_button.clicked.connect(self.pause_stopwatch)
        reset_button.clicked.connect(self.reset_stopwatch)

        buttons = QHBoxLayout()
        buttons.addWidget(start_button)
        buttons.addWidget(pause_button)
        buttons.addWidget(reset_button)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.stopwatch_label)
        layout.addLayout(buttons)
        layout.addStretch()

        self.tabs.addTab(tab, "⏱ Stopwatch")

    def start_stopwatch(self):
        self.stopwatch_running = True

    def pause_stopwatch(self):
        self.stopwatch_running = False

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        self.update_stopwatch_display()

    def update_stopwatch_display(self):
        hours = self.stopwatch_seconds // 3600
        minutes = (self.stopwatch_seconds % 3600) // 60
        seconds = self.stopwatch_seconds % 60
        self.stopwatch_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    # ==========================================================
    # COUNTDOWN TIMER TAB
    # ==========================================================
    def create_timer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        title = QLabel("COUNTDOWN TIMER")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22))

        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 70, QFont.Bold))

        self.timer_minutes = QSpinBox()
        self.timer_minutes.setRange(0, 999)
        self.timer_minutes.setValue(5)
        self.timer_minutes.setSuffix(" min")

        self.timer_seconds_input = QSpinBox()
        self.timer_seconds_input.setRange(0, 59)
        self.timer_seconds_input.setSuffix(" sec")

        set_button = QPushButton("SET TIMER")
        start_button = QPushButton("▶ START")
        pause_button = QPushButton("⏸ PAUSE")
        reset_button = QPushButton("↻ RESET")

        set_button.clicked.connect(self.set_timer)
        start_button.clicked.connect(self.start_timer)
        pause_button.clicked.connect(self.pause_timer)
        reset_button.clicked.connect(self.reset_timer)

        inputs = QHBoxLayout()
        inputs.addWidget(self.timer_minutes)
        inputs.addWidget(self.timer_seconds_input)

        buttons = QHBoxLayout()
        buttons.addWidget(start_button)
        buttons.addWidget(pause_button)
        buttons.addWidget(reset_button)

        layout.addWidget(title)
        layout.addWidget(self.timer_label)
        layout.addLayout(inputs)
        layout.addWidget(set_button)
        layout.addLayout(buttons)
        layout.addStretch()

        self.tabs.addTab(tab, "⏳ Timer")

    def set_timer(self):
        self.timer_seconds = (
            self.timer_minutes.value() * 60 + self.timer_seconds_input.value()
        )
        self.timer_running = False
        self.update_timer_display()

    def start_timer(self):
        if self.timer_seconds > 0:
            self.timer_running = True

    def pause_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 0
        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    # ==========================================================
    # ALARM TAB
    # ==========================================================
    def create_alarm_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        title = QLabel("ALARMS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 26))

        self.alarm_time_edit = QTimeEdit()
        self.alarm_time_edit.setDisplayFormat("HH:mm")
        self.alarm_time_edit.setTime(QTime.currentTime())

        ringtone_button = QPushButton("🎵 CHOOSE RINGTONE")
        ringtone_button.clicked.connect(self.choose_ringtone)

        self.ringtone_label = QLabel("Default system sound")
        self.ringtone_label.setAlignment(Qt.AlignCenter)

        volume_text = QLabel("🔊 Alarm Volume")
        volume_text.setAlignment(Qt.AlignCenter)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.change_volume)

        add_button = QPushButton("➕ ADD ALARM")
        edit_button = QPushButton("✏️ EDIT SELECTED")
        delete_button = QPushButton("🗑 DELETE SELECTED")
        stop_button = QPushButton("⏹ STOP SOUND")
        snooze_button = QPushButton("😴 SNOOZE 5 MIN")

        add_button.clicked.connect(self.add_alarm)
        edit_button.clicked.connect(self.edit_alarm)
        delete_button.clicked.connect(self.delete_alarm)
        stop_button.clicked.connect(self.stop_alarm_sound)
        snooze_button.clicked.connect(self.snooze_selected)

        self.alarm_list = QListWidget()

        layout.addWidget(title)
        layout.addWidget(self.alarm_time_edit)
        layout.addWidget(ringtone_button)
        layout.addWidget(self.ringtone_label)
        layout.addWidget(volume_text)
        layout.addWidget(self.volume_slider)
        layout.addWidget(add_button)
        layout.addWidget(self.alarm_list)

        buttons1 = QHBoxLayout()
        buttons1.addWidget(edit_button)
        buttons1.addWidget(delete_button)

        buttons2 = QHBoxLayout()
        buttons2.addWidget(snooze_button)
        buttons2.addWidget(stop_button)

        layout.addLayout(buttons1)
        layout.addLayout(buttons2)

        self.tabs.addTab(tab, "🔔 Alarms")

    def choose_ringtone(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Alarm Ringtone",
            "",
            "Audio Files (*.mp3 *.wav *.m4a *.ogg *.aac)",
        )
        if file_path:
            self.alarm_sound = file_path
            self.ringtone_label.setText("🎵 " + os.path.basename(file_path))

    def change_volume(self, value):
        self.audio_output.setVolume(value / 100)

    def add_alarm(self):
        selected_time = self.alarm_time_edit.time()
        alarm_time = selected_time.toString("HH:mm")

        alarm = {
            "time": alarm_time,
            "enabled": True,
            "sound": self.alarm_sound,
            "volume": self.volume_slider.value(),
            "snoozed_until": None,
        }

        self.alarms.append(alarm)
        self.refresh_alarm_list()

    def refresh_alarm_list(self):
        self.alarm_list.clear()
        for index, alarm in enumerate(self.alarms):
            status = "ON" if alarm["enabled"] else "OFF"
            sound_name = "Default"
            if alarm["sound"]:
                sound_name = os.path.basename(alarm["sound"])

            text = f"{alarm['time']}   •   {status}\n🎵 {sound_name}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, index)
            self.alarm_list.addItem(item)

    def edit_alarm(self):
        item = self.alarm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Edit Alarm", "Select an alarm first.")
            return

        index = item.data(Qt.UserRole)
        alarm = self.alarms[index]

        time = QTime.fromString(alarm["time"], "HH:mm")
        self.alarm_time_edit.setTime(time)
        self.alarm_sound = alarm["sound"]

        self.ringtone_label.setText(
            "🎵 "
            + (
                os.path.basename(self.alarm_sound)
                if self.alarm_sound
                else "Default system sound"
            )
        )
        self.volume_slider.setValue(alarm["volume"])

        self.alarms.pop(index)
        self.refresh_alarm_list()

    def delete_alarm(self):
        item = self.alarm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Delete Alarm", "Select an alarm first.")
            return

        index = item.data(Qt.UserRole)
        self.alarms.pop(index)
        self.refresh_alarm_list()

    def snooze_selected(self):
        item = self.alarm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Snooze", "Select an alarm first.")
            return

        index = item.data(Qt.UserRole)
        alarm = self.alarms[index]

        now = datetime.now()
        snooze_time = now + timedelta(minutes=5)

        alarm["snoozed_until"] = snooze_time
        alarm["enabled"] = True
        self.refresh_alarm_list()

    def stop_alarm_sound(self):
        self.player.stop()

    def play_alarm(self, alarm):
        sound = alarm["sound"]
        volume = alarm["volume"]

        self.audio_output.setVolume(volume / 100)

        if sound and os.path.exists(sound):
            self.player.setSource(QUrl.fromLocalFile(sound))
            self.player.play()
        else:
            QApplication.beep()

    def play_timer_sound(self):
        if self.alarm_sound and os.path.exists(self.alarm_sound):
            self.player.setSource(QUrl.fromLocalFile(self.alarm_sound))
            self.player.play()
        else:
            QApplication.beep()

    def check_alarms(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        for alarm in self.alarms:
            if not alarm["enabled"]:
                continue

            snoozed_until = alarm["snoozed_until"]
            if snoozed_until:
                if now >= snoozed_until:
                    alarm["snoozed_until"] = None
                    self.trigger_alarm(alarm)
                continue

            if alarm["time"] == current_time:
                last_triggered = alarm.get("last_triggered")
                current_minute = now.strftime("%Y-%m-%d %H:%M")

                if last_triggered == current_minute:
                    continue

                alarm["last_triggered"] = current_minute
                self.trigger_alarm(alarm)

    def trigger_alarm(self, alarm):
        self.play_alarm(alarm)

        message = QMessageBox(self)
        message.setWindowTitle("🔔 ALARM")
        message.setText(f"⏰ Alarm!\n\nIt is {alarm['time']}")

        snooze_button = message.addButton(
            "😴 Snooze 5 Minutes", QMessageBox.AcceptRole
        )
        stop_button = message.addButton("⏹ Stop", QMessageBox.RejectRole)

        message.exec()

        clicked = message.clickedButton()
        if clicked == snooze_button:
            alarm["snoozed_until"] = datetime.now() + timedelta(minutes=5)
            self.player.stop()
        else:
            self.player.stop()

    # ==========================================================
    # MAIN LOOP TICK
    # ==========================================================
    def update_everything(self):
        now = datetime.now()

        # Update Live Clock
        self.clock_label.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%A, %d %B %Y"))

        # Update Stopwatch
        if self.stopwatch_running:
            self.stopwatch_seconds += 1
            self.update_stopwatch_display()

        # Update Countdown Timer
        if self.timer_running:
            if self.timer_seconds > 0:
                self.timer_seconds -= 1
                self.update_timer_display()
            else:
                self.timer_running = False
                self.play_timer_sound()
                QMessageBox.information(
                    self, "⏰ Timer Finished", "Your timer has finished!"
                )

        # Check Alarms
        self.check_alarms()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClockApp()
    window.show()
    sys.exit(app.exec())