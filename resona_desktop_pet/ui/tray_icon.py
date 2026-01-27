from pathlib import Path
from typing import Optional, Callable
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from ..config import ConfigManager

class TrayIcon(QSystemTrayIcon):
    def __init__(self, config: ConfigManager, show_callback: Optional[Callable] = None, settings_callback: Optional[Callable] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.project_root = Path(config.config_path).parent
        self._show_callback = show_callback
        self._settings_callback = settings_callback
        self._setup_icon()
        self._setup_menu()
        self.activated.connect(self._on_activated)

    def _setup_icon(self):
        icon_path = Path(self.config.tray_icon_path)
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)
            self.setIcon(QIcon(pixmap))
        self.setToolTip(f"Resona Desktop Pet - {self.config.character_name}")

    def _setup_menu(self):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #2d2d2d; border: 1px solid #555; border-radius: 5px; padding: 5px; } QMenu::item { color: white; padding: 8px 25px; border-radius: 3px; } QMenu::item:selected { background-color: #404040; } QMenu::separator { height: 1px; background: #555; margin: 5px 10px; }")
        
        show_action = QAction("Show Resona", self)
        show_action.triggered.connect(self._on_show)
        menu.addAction(show_action)
        menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._on_settings)
        menu.addAction(settings_action)
        menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        self.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick: self._on_show()

    def _on_show(self):
        if self._show_callback: self._show_callback()

    def _on_settings(self):
        if self._settings_callback: self._settings_callback()

    def show_message(self, title: str, message: str, icon_type=None):
        if icon_type is None: icon_type = QSystemTrayIcon.MessageIcon.Information
        self.showMessage(title, message, icon_type, 3000)