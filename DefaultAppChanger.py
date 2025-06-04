import os
import sys
import re
import shutil
import logging


from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QScrollArea,
    QComboBox, QCheckBox, QPushButton, QMessageBox, QGridLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


APP_FOLDER = "/Applications"
SYSTEM_APP_FOLDER = "/System/Applications"

CATEGORIES = {
    "基础文本格式": sorted([".txt", ".csv", ".tsv", ".json", ".xml", ".yaml", ".yml", ".ini", ".conf", ".toml", ".log"]),
    "编程语言格式": sorted([
        ".c", ".cpp", ".h", ".hpp", ".java", ".py", ".js", ".mjs", ".cjs", ".ts", ".html", ".css",
        ".php", ".rb", ".go", ".rs", ".swift", ".kt", ".kts", ".sh", ".bash", ".zsh", ".lua", 
        ".sql", ".ddl", ".dml", ".r", ".R", ".m"
        ], key=str.lower),
    "标记语言格式": sorted([".md", ".rst", ".tex"]),
    "其他": sorted([".plist", ".gitconfig", ".dockerfile", ".makefile", ".dockerignore", ".gitattributes", ".gitignore", ".editorconfig"])
}

pattern = r'(text|edit|code|note|studio|ide|vim|charm|emacs|cursor|markdown)'

def app_list():
    """ 
    获取 /Applications 和 /System/Applications 中的所有应用程序名称
    Returns:
        list -- 排序后的应用程序列表
    """
    app_list = {}
    user_app_list = os.listdir(APP_FOLDER)
    for app in user_app_list:
        if app.endswith('.app') and not app.startswith('.'):
            icon = get_icon(APP_FOLDER, app)
            app_list.update({app: icon})
    all_app_list = os.listdir(SYSTEM_APP_FOLDER) 
    for app in all_app_list:
        if app.endswith('.app') and not app.startswith('.'):
            icon = get_icon(SYSTEM_APP_FOLDER, app)
            app_list.update({app: icon})
    
    # 过滤掉不需要的应用程序
    app_list = {app: icon for app, icon in app_list.items() if re.search(pattern, app, re.IGNORECASE)}
    app_list = dict(sorted(app_list.items()))

    return app_list


def get_appid(app):
    cmd = "osascript -e 'id of app \"" + app + "\"'"
    resp = os.popen(cmd).read().splitlines()
    resp = resp[0] if len(resp) > 0 else None
    return resp


def duti(appid, ext):
    is_bundled = hasattr(sys, '_MEIPASS')
    if is_bundled:
        base_path = os.path.dirname(sys.executable)
        duti_app = os.path.join(base_path, '../Resources/resources/duti')
        # duti_app = '/opt/homebrew/bin/duti'
    else:
        duti_app = os.path.join(os.path.dirname(__file__), 'resources', 'duti')
        if not os.path.exists(duti_app):
            duti_app = shutil.which('duti')

    if not duti_app or not os.path.exists(duti_app):
        logging.error("未找到 duti 命令")
        return False
    resp = os.system(f"{duti_app} -s " + appid + " " + ext + " all")
    return True if resp == 0 else False

def get_icon(app_dir, app_name):
    app_path = os.path.join(app_dir, app_name)
    icon_path_folder = os.path.join(app_path, 'Contents/Resources')
    if os.path.exists(icon_path_folder):
        for i in os.listdir(icon_path_folder):
            if i.endswith('.icns'):
                icon_path = os.path.join(icon_path_folder, i)
                return QIcon(icon_path)

    # 如果没有找到 .icns 文件，返回默认图标
    return QIcon()
     


def modify(selected_app, selected_items) -> None:
    """
    将选中的文件打开方式更改为选定的app
    Args:
        selected_app (str): 选定的应用程序名称
        selected_items (list): 选中的文件类型列表
    """
    appid = get_appid(selected_app)
    failed = []
    if appid is None:
        logging.error(f"无法获取应用程序 {selected_app} 的应用ID")
        failed.append(f"无法获取应用程序 {selected_app} 的应用ID")

    for item in selected_items:
        if not duti(appid, item):
            logging.error(f"无法将 {item} 的打开方式更改为 {selected_app}")
            failed.append(item)
        else:
            logging.info(f"{item} 的打开方式已更改为 {selected_app}")
    return failed
    

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.apps = app_list()
        self.checkboxes = {}         # 子项: QCheckBox
        self.group_checkboxes = {}   # 类别: QCheckBox
        # self.check_duti()
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle("Default Apps Changer")
        layout = QVBoxLayout()

        # 应用选择
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("应用选择："))
        self.app_list_cb = QComboBox()
        for app, icon in self.apps.items():
            self.app_list_cb.addItem(icon, app)
        # self.app_list_cb.addItems(self.apps)
        self.app_list_cb.setCurrentText("TextEdit.app")  # 默认选择 TextEdit
        hbox.addWidget(self.app_list_cb)
        layout.addLayout(hbox)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for category, items in CATEGORIES.items():
            group_box = QGroupBox()
            group_layout = QVBoxLayout()

            # 大类 checkbox
            group_cb = QCheckBox(category)
            group_cb.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            group_cb.stateChanged.connect(self.make_toggle_category(category))
            self.group_checkboxes[category] = group_cb
            group_layout.addWidget(group_cb)

            # 子类 checkbox 网格
            grid = QGridLayout()
            for idx, item in enumerate(items):
                cb = QCheckBox(item)
                cb.setStyleSheet("padding-left: 20px;")  # 缩进
                cb.stateChanged.connect(self.update_apply_button_state)
                self.checkboxes[item] = cb
                row, col = divmod(idx, 3)  # 每行3个
                grid.addWidget(cb, row, col)
            group_layout.addLayout(grid)
            group_box.setLayout(group_layout)
            scroll_layout.addWidget(group_box)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # 控制按钮
        button_layout = QHBoxLayout()
        self.selectAllButton = QPushButton("全选/取消")
        self.selectAllButton.clicked.connect(self.toggle_all)
        self.inverseButton = QPushButton("反选")
        self.inverseButton.clicked.connect(self.inverse_select)
        button_layout.addWidget(self.selectAllButton)
        button_layout.addWidget(self.inverseButton)
        layout.addLayout(button_layout)

        # 应用按钮
        self.applyButton = QPushButton("更改打开方式")
        self.applyButton.setEnabled(False)
        self.applyButton.clicked.connect(self.apply)
        layout.addWidget(self.applyButton)

        self.setLayout(layout)

    def make_toggle_category(self, category):
        def toggle(state):
            is_checked = Qt.CheckState(state) == Qt.CheckState.Checked
            for item in CATEGORIES[category]:
                self.checkboxes[item].blockSignals(True)
                self.checkboxes[item].setChecked(is_checked)
                self.checkboxes[item].blockSignals(False)
            self.update_apply_button_state()
        return toggle

    def toggle_all(self):
        all_checked = all(cb.isChecked() for cb in self.checkboxes.values())
        for cb in self.checkboxes.values():
            cb.setChecked(not all_checked)

    def inverse_select(self):
        for cb in self.checkboxes.values():
            cb.setChecked(not cb.isChecked())

    def update_apply_button_state(self):
        any_checked = any(cb.isChecked() for cb in self.checkboxes.values())
        self.applyButton.setEnabled(any_checked)

    # def check_duti(self):
    #     is_bundled = hasattr(sys, '_MEIPASS')
    #     if is_bundled:
    #         duti_app = '/opt/homebrew/bin/duti'
    #     else:
    #         duti_app = shutil.which('duti')

    #     if not duti_app or not os.path.exists(duti_app):
    #         QMessageBox.information(self, "错误", "duti 命令未找到，请安装 duti： \n brew install duti")
    #         sys.exit(1)
        

    def apply(self):
        selected_app = self.app_list_cb.currentText()
        selected_types = [name for name, cb in self.checkboxes.items() if cb.isChecked()]
        failed = modify(selected_app, selected_types)
        if not failed:
            QMessageBox.information(self, "成功", "所有类型设置成功！")
        else:
            QMessageBox.warning(self, "失败", f"以下类型设置失败：\n" + "\n".join(failed))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


