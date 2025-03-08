# Installer les dépendances : pip install ffmpeg-python PyQt5
import ffmpeg
import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QFileDialog, QLineEdit, QComboBox, QVBoxLayout, 
                            QHBoxLayout, QWidget, QMessageBox, QGroupBox, QFormLayout,
                            QSlider, QDialog, QStyle)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class VideoAudioEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.input_path = ""
        self.output_path = ""
        
    def initUI(self):
        self.setWindowTitle("Éditeur Vidéo/Audio")
        self.setGeometry(300, 300, 600, 400)
        
        # Widget principal
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Groupe pour les fichiers
        file_group = QGroupBox("Fichiers")
        file_layout = QFormLayout()
        
        # Entrée vidéo
        self.input_label = QLabel("Fichier d'entrée:")
        self.input_text = QLineEdit()
        self.input_text.setReadOnly(True)
        self.input_browse = QPushButton("Parcourir")
        self.input_browse.clicked.connect(self.browse_input)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.input_browse)
        file_layout.addRow(self.input_label, input_layout)
        
        # Sortie vidéo/audio
        self.output_label = QLabel("Fichier de sortie:")
        self.output_text = QLineEdit()
        self.output_text.setReadOnly(True)
        self.output_browse = QPushButton("Parcourir")
        self.output_browse.clicked.connect(self.browse_output)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_text)
        output_layout.addWidget(self.output_browse)
        file_layout.addRow(self.output_label, output_layout)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Groupe pour les paramètres
        params_group = QGroupBox("Paramètres")
        params_layout = QFormLayout()
        
        # Type de sortie (vidéo ou audio)
        self.output_type_label = QLabel("Type de sortie:")
        self.output_type = QComboBox()
        self.output_type.addItems(["Vidéo", "Audio MP3", "Audio WAV"])
        self.output_type.currentIndexChanged.connect(self.update_output_extension)
        params_layout.addRow(self.output_type_label, self.output_type)
        
        # Temps de début avec bouton de sélection
        start_time_layout = QHBoxLayout()
        self.start_time_label = QLabel("Temps de début (mm:ss):")
        self.start_time = QLineEdit("00:00")
        self.start_time_btn = QPushButton("Marquer début")
        self.start_time_btn.clicked.connect(self.mark_start_time)
        start_time_layout.addWidget(self.start_time)
        start_time_layout.addWidget(self.start_time_btn)
        params_layout.addRow(self.start_time_label, start_time_layout)
        
        # Temps de fin avec bouton de sélection
        end_time_layout = QHBoxLayout()
        self.end_time_label = QLabel("Temps de fin (mm:ss):")
        self.end_time = QLineEdit("00:10")
        self.end_time_btn = QPushButton("Marquer fin")
        self.end_time_btn.clicked.connect(self.mark_end_time)
        end_time_layout.addWidget(self.end_time)
        end_time_layout.addWidget(self.end_time_btn)
        params_layout.addRow(self.end_time_label, end_time_layout)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # Bouton pour exécuter
        self.process_button = QPushButton("Traiter")
        self.process_button.clicked.connect(self.process_media)
        main_layout.addWidget(self.process_button)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def browse_input(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Sélectionner un fichier vidéo", "", 
            "Fichiers vidéo (*.mp4 *.avi *.mkv *.mov);;Tous les fichiers (*.*)"
        )
        
        if file_path:
            self.input_path = file_path
            self.input_text.setText(file_path)
            
            # Mettre à jour le chemin de sortie par défaut
            if not self.output_path:
                base_dir = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                extension = self.get_output_extension()
                self.output_path = os.path.join(base_dir, f"{base_name}_modifie{extension}")
                self.output_text.setText(self.output_path)
    
    def browse_output(self):
        # Déterminer les filtres de fichiers en fonction du type de sortie
        if self.output_type.currentText() == "Audio MP3":
            file_filter = "Fichiers MP3 (*.mp3)"
            default_ext = ".mp3"
        elif self.output_type.currentText() == "Audio WAV":
            file_filter = "Fichiers WAV (*.wav)"
            default_ext = ".wav"
        else:
            file_filter = "Fichiers vidéo (*.mp4)"
            default_ext = ".mp4"
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Choisir le fichier de sortie", "", file_filter
        )
        
        if file_path:
            # S'assurer que l'extension est correcte
            if not file_path.endswith(default_ext):
                file_path += default_ext
                
            self.output_path = file_path
            self.output_text.setText(file_path)
    
    def get_output_extension(self):
        if self.output_type.currentText() == "Audio MP3":
            return ".mp3"
        elif self.output_type.currentText() == "Audio WAV":
            return ".wav"
        else:
            return ".mp4"
            
    def update_output_extension(self):
        if not self.input_path:
            return
            
        # Mettre à jour l'extension du fichier de sortie quand le type change
        if self.output_path:
            base_dir = os.path.dirname(self.output_path)
            base_name = os.path.splitext(os.path.basename(self.output_path))[0]
            
            extension = self.get_output_extension()
            self.output_path = os.path.join(base_dir, f"{base_name}{extension}")
            self.output_text.setText(self.output_path)
    
    def mark_start_time(self):
        if not self.input_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un fichier d'entrée")
            return
        
        # Ouvrir la fenêtre de prévisualisation pour sélectionner le temps de début
        time_marker = TimeMarkerDialog(self.input_path, self)
        if time_marker.exec_() == QDialog.Accepted:
            self.start_time.setText(time_marker.get_time_str())
    
    def mark_end_time(self):
        if not self.input_path:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord sélectionner un fichier d'entrée")
            return
        
        # Ouvrir la fenêtre de prévisualisation pour sélectionner le temps de fin
        time_marker = TimeMarkerDialog(self.input_path, self)
        if time_marker.exec_() == QDialog.Accepted:
            self.end_time.setText(time_marker.get_time_str())
    
    def process_media(self):
        if not self.input_path:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un fichier d'entrée")
            return
        
        if not self.output_path:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un fichier de sortie")
            return
        
        start_time = self.start_time.text()
        end_time = self.end_time.text()
        
        try:
            output_type = self.output_type.currentText()
            
            if output_type == "Vidéo":
                couper_video(self.input_path, self.output_path, start_time, end_time)
            elif output_type == "Audio MP3":
                extraire_audio(self.input_path, self.output_path, start_time, end_time, "mp3")
            elif output_type == "Audio WAV":
                extraire_audio(self.input_path, self.output_path, start_time, end_time, "wav")
                
            QMessageBox.information(self, "Succès", f"Le fichier a été traité avec succès et sauvegardé sous:\n{self.output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors du traitement: {str(e)}")


def couper_video(input_path, output_path, start_time, end_time):
    """
    Coupe une vidéo entre start_time et end_time.
    
    :param input_path: Chemin de la vidéo d'entrée
    :param output_path: Chemin de la vidéo de sortie
    :param start_time: Temps de début (format mm:ss)
    :param end_time: Temps de fin (format mm:ss)
    """
    # Vérifier si le fichier existe
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    (
        ffmpeg
        .input(input_path, ss=start_time)
        .output(output_path, to=end_time, c='copy')
        .run()
    )


def extraire_audio(input_path, output_path, start_time, end_time, format_audio="mp3"):
    """
    Extrait l'audio d'une vidéo entre start_time et end_time.
    
    :param input_path: Chemin de la vidéo d'entrée
    :param output_path: Chemin du fichier audio de sortie
    :param start_time: Temps de début (format mm:ss)
    :param end_time: Temps de fin (format mm:ss)
    :param format_audio: Format de l'audio (mp3 ou wav)
    """
    # Vérifier si le fichier existe
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier {input_path} n'existe pas")
    
    # Configurer les paramètres audio selon le format
    if format_audio == "mp3":
        audio_codec = "libmp3lame"
        audio_quality = "2"  # Qualité moyenne-haute (0-9, 0 étant la meilleure)
    else:  # wav
        audio_codec = "pcm_s16le"  # PCM 16 bits
        audio_quality = None
    
    stream = ffmpeg.input(input_path, ss=start_time)
    
    if end_time and end_time != "00:00":
        # Calculer la durée à partir du début
        stream = stream.output(output_path, to=end_time, acodec=audio_codec)
    else:
        # Pas de temps de fin spécifié, prendre jusqu'à la fin
        stream = stream.output(output_path, acodec=audio_codec)
    
    # Ajouter la qualité si c'est du MP3
    if audio_quality:
        stream = stream.global_args('-q:a', audio_quality)
    
    stream.run()


class TimeMarkerDialog(QDialog):
    """Dialogue pour sélectionner visuellement un point dans le temps d'une vidéo ou audio"""
    
    def __init__(self, media_file, parent=None):
        super().__init__(parent)
        self.media_file = media_file
        self.current_time = 0
        self.duration = 0
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Sélectionnez un point dans le temps")
        self.setMinimumSize(600, 150)
        
        layout = QVBoxLayout()
        
        # Affichage du temps
        time_layout = QHBoxLayout()
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.duration_label = QLabel("/ 00:00")
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.duration_label)
        layout.addLayout(time_layout)
        
        # Slider pour naviguer dans le média
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.position_slider)
        
        # Contrôles de lecture
        control_layout = QHBoxLayout()
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_playback)
        
        self.forward_button = QPushButton("+5s")
        self.forward_button.clicked.connect(self.forward_5_seconds)
        
        self.backward_button = QPushButton("-5s")
        self.backward_button.clicked.connect(self.backward_5_seconds)
        
        control_layout.addWidget(self.backward_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.forward_button)
        
        layout.addLayout(control_layout)
        
        # Boutons OK/Annuler
        buttons_layout = QHBoxLayout()
        self.select_button = QPushButton("Sélectionner ce point")
        self.select_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Initialiser le lecteur média (en utilisant une alternative à QMediaPlayer car il peut ne pas être disponible)
        self.setup_media_player()
        
    def setup_media_player(self):
        """Initialise soit QMediaPlayer, soit une alternative basée sur ffmpeg"""
        try:
            # Essayer d'utiliser QMediaPlayer si disponible
            self.media_player = QMediaPlayer()
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.media_file)))
            self.media_player.positionChanged.connect(self.position_changed)
            self.media_player.durationChanged.connect(self.duration_changed)
            self.use_qt_player = True
        except:
            # Alternative: obtenir la durée via ffmpeg
            self.use_qt_player = False
            try:
                # Obtenir la durée en secondes avec ffmpeg
                cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
                      '-of', 'default=noprint_wrappers=1:nokey=1', self.media_file]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.stdout:
                    self.duration = float(result.stdout.strip())
                    self.position_slider.setRange(0, int(self.duration * 1000))
                    self.duration_label.setText(f"/ {self.format_time(int(self.duration * 1000))}")
            except Exception as e:
                QMessageBox.warning(self, "Attention", f"Impossible de déterminer la durée du média: {str(e)}")
    
    def toggle_playback(self):
        """Alterne entre lecture et pause"""
        if self.use_qt_player:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            else:
                self.media_player.play()
                self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
    
    def position_changed(self, position):
        """Met à jour l'interface quand la position change"""
        self.current_time = position
        self.position_slider.setValue(position)
        self.time_label.setText(self.format_time(position))
    
    def duration_changed(self, duration):
        """Met à jour l'interface quand la durée est déterminée"""
        self.duration = duration
        self.position_slider.setRange(0, duration)
        self.duration_label.setText(f"/ {self.format_time(duration)}")
    
    def set_position(self, position):
        """Définit la position de lecture"""
        if self.use_qt_player:
            self.media_player.setPosition(position)
        else:
            self.current_time = position
            self.time_label.setText(self.format_time(position))
    
    def forward_5_seconds(self):
        """Avance de 5 secondes"""
        if self.use_qt_player:
            new_pos = min(self.media_player.position() + 5000, self.duration)
            self.media_player.setPosition(new_pos)
        else:
            new_pos = min(self.current_time + 5000, self.duration * 1000)
            self.current_time = new_pos
            self.position_slider.setValue(int(new_pos))
            self.time_label.setText(self.format_time(int(new_pos)))
    
    def backward_5_seconds(self):
        """Recule de 5 secondes"""
        if self.use_qt_player:
            new_pos = max(self.media_player.position() - 5000, 0)
            self.media_player.setPosition(new_pos)
        else:
            new_pos = max(self.current_time - 5000, 0)
            self.current_time = new_pos
            self.position_slider.setValue(int(new_pos))
            self.time_label.setText(self.format_time(int(new_pos)))
    
    def format_time(self, ms):
        """Convertit des millisecondes en format mm:ss"""
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"
    
    def get_time_str(self):
        """Renvoie le temps actuel au format mm:ss"""
        if self.use_qt_player:
            ms = self.media_player.position()
        else:
            ms = self.current_time
        return self.format_time(ms)
    
    def closeEvent(self, event):
        """Arrête le lecteur avant de fermer"""
        if self.use_qt_player:
            self.media_player.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VideoAudioEditor()
    editor.show()
    sys.exit(app.exec_())