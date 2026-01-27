import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QLabel, QGroupBox, QLineEdit, 
                             QDoubleSpinBox, QSpinBox, QCheckBox, QComboBox, QTreeWidget,
                             QTreeWidgetItem, QFormLayout, QMessageBox, QTextEdit, QStatusBar)
from PySide6.QtCore import Qt

TRANSLATIONS = {
    "AND": {"label": "所有条件满足(AND)", "fields": []},
    "OR": {"label": "任一条件满足(OR)", "fields": []},
    "CUMULATIVE": {"label": "累计满足(曾达成即可)", "fields": []},
    "cpu_temp": {"label": "CPU温度(>)", "fields": ["gt"]},
    "gpu_temp": {"label": "GPU温度(>)", "fields": ["gt"]},
    "cpu_usage": {"label": "CPU占用(%)", "fields": ["gt"]},
    "gpu_usage": {"label": "GPU占用(%)", "fields": ["gt"]},
    "idle_duration": {"label": "闲置时长(s)", "fields": ["sec"]},
    "idle_recovery": {"label": "闲置结束(恢复)", "fields": ["sec"]},
    "process_active": {"label": "进程在前台", "fields": ["pnames"]},
    "process_background": {"label": "进程在运行", "fields": ["pnames", "only_new"]},
    "clip_match": {"label": "剪贴板内容匹配", "fields": ["keywords"]},
    "url_match": {"label": "浏览器URL匹配", "fields": ["keywords"]},
    "title_match": {"label": "窗口标题匹配", "fields": ["keywords"]},
    "hover_duration": {"label": "鼠标悬停(s)", "fields": ["sec"]},
    "leave_duration": {"label": "离开时长(s)", "fields": ["sec"]},
    "long_press": {"label": "长按立绘(s)", "fields": ["sec"]},
    "click_count": {"label": "点击连击数", "fields": ["count", "duration"]},
    "fullscreen": {"label": "进入全屏模式", "fields": []},
    "weather_match": {"label": "天气匹配", "fields": ["keywords"]},
    "music_match": {"label": "音乐匹配(网易云)", "fields": ["keywords", "only_on_change"]},
    "date_match": {"label": "日期匹配(MM-DD)", "fields": ["date"]},
    "time_range": {"label": "时间段(HH:MM-HH:MM)", "fields": ["range"]},
    "speak": {"label": "语音台词", "fields": ["text", "emotion", "voice_file"]},
    "delay": {"label": "延迟等待", "fields": ["sec"]},
    "move_to": {"label": "移动位置", "fields": ["pos"]},
    "fade_out": {"label": "虚化/透明度", "fields": ["opacity", "sec", "hover_recovery"]},
    "lock_interaction": {"label": "锁定交互(无法点击)", "fields": ["sec"]},
    "random_group": {"label": "随机动作分支", "fields": ["branches"]},
    "exit_app": {"label": "退出程序", "fields": []},
    "keywords": "关键词列表",
    "pnames": "进程名列表",
    "gt": "大于数值",
    "sec": "秒数",
    "count": "次数",
    "duration": "持续时间(s)",
    "range": "范围",
    "date": "日期",
    "opacity": "透明度",
    "weight": "随机权重",
    "only_new": "仅检测新启动",
    "only_on_change": "仅切歌时触发一次",
    "hover_recovery": "悬停恢复时间(s)",
    "text": "文本内容",
    "emotion": "情感标签",
    "voice_file": "音频文件名(可选)",
    "pos": "位置(top_left/bottom_right)",
    "branches": "分支列表(JSON)"
}

EMOTION_TAGS = [
    "<E:smile>", "<E:angry>", "<E:sad>", "<E:serious>", "<E:thinking>",
    "<E:surprised>", "<E:dislike>", "<E:smirk>", "<E:embarrassed>"
]

ACT_TYPES = {k: v for k, v in TRANSLATIONS.items() if k in ["speak", "delay", "random_group", "move_to", "fade_out", "exit_app", "lock_interaction"]}
COND_TYPES = {k: v for k, v in TRANSLATIONS.items() if isinstance(v, dict) and k not in ACT_TYPES and k not in ["AND", "OR", "CUMULATIVE"]}

class TriggerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interaction Trigger Editor")
        self.resize(1300, 850)
        self.project_root = Path(__file__).parent.parent
        self.current_triggers = []
        self.selected_index = -1
        self.active_pack_id = ""
        self.editing_item_ref = None
        self.editing_tree_item_ref = None
        self.init_ui()
        self.setStatusBar(QStatusBar(self))
        self.scan_packs()
        self.load_data()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        left_panel = QVBoxLayout()
        pack_group = QGroupBox("📦 资源包选择")
        pack_layout = QHBoxLayout(pack_group)
        self.pack_combo = QComboBox()
        self.pack_combo.currentTextChanged.connect(self.on_pack_changed)
        pack_layout.addWidget(self.pack_combo)
        left_panel.addWidget(pack_group)
        left_panel.addWidget(QLabel("触发器列表:"))
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_trigger_selected)
        left_panel.addWidget(self.list_widget)
        btn_add_trigger = QPushButton("➕ 新增触发器")
        btn_add_trigger.clicked.connect(self.add_trigger)
        btn_del_trigger = QPushButton("❌ 删除选中")
        btn_del_trigger.clicked.connect(self.delete_trigger)
        left_panel.addWidget(btn_add_trigger)
        left_panel.addWidget(btn_del_trigger)
        layout.addLayout(left_panel, 1)
        mid_panel = QVBoxLayout()
        base_gb = QGroupBox("1. 触发器基础信息")
        f1 = QFormLayout(base_gb)
        self.id_edit = QLineEdit()
        self.id_edit.textChanged.connect(lambda t: self._update_base_val("id", t))
        self.desc_edit = QLineEdit()
        self.desc_edit.textChanged.connect(lambda t: self._update_base_val("description", t))
        self.logic_box = QComboBox()
        self.logic_box.addItems(["AND", "OR", "CUMULATIVE"])
        self.logic_box.currentTextChanged.connect(lambda t: self._update_base_val("logic", t))
        self.prob_spin = QDoubleSpinBox(); self.prob_spin.setRange(0.0, 1.0); self.prob_spin.setSingleStep(0.05)
        self.prob_spin.valueChanged.connect(lambda v: self._update_base_val("probability", v))
        self.cd_spin = QSpinBox(); self.cd_spin.setRange(0, 3600)
        self.cd_spin.valueChanged.connect(lambda v: self._update_base_val("cooldown", v))
        self.max_spin = QSpinBox(); self.max_spin.setRange(0, 9999)
        self.max_spin.valueChanged.connect(lambda v: self._update_base_val("max_triggers", v))
        self.startup_cb = QCheckBox("仅启动时触发")
        self.startup_cb.toggled.connect(lambda b: self._update_base_val("startup_only", b))
        f1.addRow("ID:", self.id_edit)
        f1.addRow("规则描述:", self.desc_edit)
        f1.addRow("判定逻辑:", self.logic_box)
        f1.addRow("触发概率:", self.prob_spin)
        f1.addRow("冷却间隔:", self.cd_spin)
        f1.addRow("每日上限:", self.max_spin)
        f1.addRow(self.startup_cb)
        mid_panel.addWidget(base_gb)
        cond_gb = QGroupBox("2. 触发判定条件 (Conditions)")
        cv = QVBoxLayout(cond_gb)
        self.cond_tree = QTreeWidget(); self.cond_tree.setHeaderLabels(["类型", "详情描述"])
        self.cond_tree.itemClicked.connect(self.on_cond_clicked)
        cv.addWidget(self.cond_tree)
        c_row = QHBoxLayout()
        self.c_type = QComboBox()
        for k in sorted(COND_TYPES.keys()):
            self.c_type.addItem(COND_TYPES[k]["label"], k)
        btn_add_c = QPushButton("添加条件"); btn_add_c.clicked.connect(self.add_condition)
        btn_del_c = QPushButton("删除选中"); btn_del_c.clicked.connect(self.delete_condition)
        c_row.addWidget(self.c_type); c_row.addWidget(btn_add_c); c_row.addWidget(btn_del_c)
        cv.addLayout(c_row)
        mid_panel.addWidget(cond_gb)
        act_gb = QGroupBox("3. 响应动作序列 (Actions)")
        av = QVBoxLayout(act_gb)
        self.act_tree = QTreeWidget(); self.act_tree.setHeaderLabels(["动作序列", "摘要"])
        self.act_tree.itemClicked.connect(self.on_act_clicked)
        av.addWidget(self.act_tree)
        a_row = QHBoxLayout()
        self.a_type = QComboBox()
        for k in sorted(ACT_TYPES.keys()):
            val = ACT_TYPES[k]
            label = val.get("label", k) if isinstance(val, dict) else val
            self.a_type.addItem(label, k)
        btn_add_a = QPushButton("插入动作"); btn_add_a.clicked.connect(self.add_action)
        btn_del_a = QPushButton("删除选中"); btn_del_a.clicked.connect(self.delete_action)
        a_row.addWidget(self.a_type); a_row.addWidget(btn_add_a); a_row.addWidget(btn_del_a)
        av.addLayout(a_row)
        mid_panel.addWidget(act_gb)
        btn_save = QPushButton("💾 保存同步 (Save to JSON)")
        btn_save.clicked.connect(self.save_data)
        btn_save.setStyleSheet("background-color: #27ae60; color: white; height: 50px; font-weight: bold;")
        mid_panel.addWidget(btn_save)
        layout.addLayout(mid_panel, 2)
        self.prop_panel = QGroupBox("属性编辑面板")
        self.prop_layout = QVBoxLayout(self.prop_panel)
        self.prop_form = QFormLayout()
        self.prop_layout.addLayout(self.prop_form)
        self.prop_layout.addStretch()
        layout.addWidget(self.prop_panel, 1)

    def scan_packs(self):
        packs_dir = self.project_root / "packs"
        if not packs_dir.exists(): return
        self.pack_combo.blockSignals(True)
        self.pack_combo.clear()
        for d in packs_dir.iterdir():
            if d.is_dir() and (d / "pack.json").exists(): self.pack_combo.addItem(d.name)
        idx = self.pack_combo.findText("Resona_Default")
        if idx >= 0: self.pack_combo.setCurrentIndex(idx)
        self.active_pack_id = self.pack_combo.currentText()
        self.pack_combo.blockSignals(False)

    def on_pack_changed(self, pack_id):
        if not pack_id: return
        self.active_pack_id = pack_id
        self.load_data()

    def load_data(self):
        if not self.active_pack_id: return
        path = self.project_root / "packs" / self.active_pack_id / "logic" / "triggers.json"
        self.current_triggers = []
        if path.exists():
            with open(path, "r", encoding="utf-8") as f: self.current_triggers = json.load(f)
        self.refresh_list()
        self.cond_tree.clear(); self.act_tree.clear()

    def save_data(self):
        if not self.active_pack_id: return
        path = self.project_root / "packs" / self.active_pack_id / "logic" / "triggers.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.current_triggers, f, indent=4, ensure_ascii=False)
        self.statusBar().showMessage(f"已成功保存至 {self.active_pack_id}", 3000)

    def refresh_list(self):
        self.list_widget.clear()
        for t in self.current_triggers: self.list_widget.addItem(t.get("id", "未命名"))

    def on_trigger_selected(self, index):
        if index < 0: return
        self.selected_index = index
        data = self.current_triggers[index]
        self.id_edit.setText(data.get("id", ""))
        self.desc_edit.setText(data.get("description", ""))
        self.logic_box.setCurrentText(data.get("logic", "AND"))
        self.prob_spin.setValue(data.get("probability", 1.0))
        self.cd_spin.setValue(data.get("cooldown", 5))
        self.max_spin.setValue(data.get("max_triggers", 9999))
        self.startup_cb.setChecked(data.get("startup_only", False))
        self.cond_tree.clear()
        self._render_recursive_conds(data.get("conditions", []), self.cond_tree.invisibleRootItem())
        self.cond_tree.expandAll()
        self.act_tree.clear()
        self._render_acts(data.get("actions", []), self.act_tree.invisibleRootItem())
        self.act_tree.expandAll()

    def add_trigger(self):
        self.current_triggers.append({"id": "new_trigger", "logic": "AND", "conditions": [], "actions": []})
        self.refresh_list()

    def delete_trigger(self):
        if self.selected_index >= 0:
            del self.current_triggers[self.selected_index]
            self.refresh_list()

    def _render_recursive_conds(self, conds, parent):
        for c in conds:
            if "logic" in c:
                item = QTreeWidgetItem(parent, [f"【逻辑组】{c['logic']}", ""])
                item.setData(0, Qt.ItemDataRole.UserRole, c)
                self._render_recursive_conds(c.get("conditions", []), item)
            else:
                label = COND_TYPES.get(c["type"], {}).get("label", c["type"])
                item = QTreeWidgetItem(parent, [label, str(c)])
                item.setData(0, Qt.ItemDataRole.UserRole, c)

    def _render_acts(self, actions, parent):
        for a in actions:
            raw_type = a["type"]
            label_def = ACT_TYPES.get(raw_type, raw_type)
            # If label_def is a dict (like our new fade_out/lock_interaction), get "label"
            label = label_def.get("label", raw_type) if isinstance(label_def, dict) else label_def
            
            item = QTreeWidgetItem(parent, [label, str(a)])
            item.setData(0, Qt.ItemDataRole.UserRole, a)

    def on_cond_clicked(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        self._build_prop_editor(data, item, COND_TYPES)

    def on_act_clicked(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        self._build_prop_editor(data, item, TRANSLATIONS)

    def _build_prop_editor(self, data, tree_item, defs):
        while self.prop_form.count():
            w = self.prop_form.takeAt(0).widget()
            if w: w.deleteLater()
        self.editing_item_ref = data; self.editing_tree_item_ref = tree_item
        item_type = data.get("type", data.get("logic"))
        
        # Determine fields definition source
        def_source = defs.get(item_type)
        if not def_source and item_type in ACT_TYPES:
             def_source = ACT_TYPES.get(item_type)
             
        fields = def_source.get("fields", []) if isinstance(def_source, dict) else []
        
        for key in fields:
            val = data.get(key)
            # Auto-fix bools that might be missing or None
            if key in ["only_new", "only_on_change"]:
                if val is None: val = False
                
            label = TRANSLATIONS.get(key, key)
            if key == "emotion":
                combo = QComboBox()
                combo.addItems(EMOTION_TAGS)
                combo.setEditable(True) # Allow custom if needed, but provide list
                idx = combo.findText(str(val))
                if idx >= 0: combo.setCurrentIndex(idx)
                else: combo.setCurrentText(str(val) if val else EMOTION_TAGS[0])
                combo.currentTextChanged.connect(lambda txt, k=key: self._update_val(k, txt))
                self.prop_form.addRow(f"{label}:", combo)
            elif isinstance(val, bool):
                cb = QCheckBox(); cb.setChecked(val)
                cb.toggled.connect(lambda v, k=key: self._update_val(k, v))
                self.prop_form.addRow(f"{label}:", cb)
            elif isinstance(val, list):
                edit = QLineEdit(", ".join(val))
                edit.textChanged.connect(lambda txt, k=key: self._update_val(k, [s.strip() for s in txt.split(",") if s.strip()]))
                self.prop_form.addRow(f"{label}:", edit)
            elif isinstance(val, (int, float)):
                spin = QDoubleSpinBox() if isinstance(val, float) else QSpinBox()
                spin.setRange(-9999, 9999); spin.setValue(val)
                spin.valueChanged.connect(lambda v, k=key: self._update_val(k, v))
                self.prop_form.addRow(f"{label}:", spin)
            else:
                edit = QLineEdit(str(val))
                edit.textChanged.connect(lambda txt, k=key: self._update_val(k, txt))
                self.prop_form.addRow(f"{label}:", edit)

    def _update_base_val(self, key, val):
        if self.selected_index >= 0:
            self.current_triggers[self.selected_index][key] = val
            if key == "id": self.refresh_list()

    def _update_val(self, key, val):
        if self.editing_item_ref:
            self.editing_item_ref[key] = val
            self.editing_tree_item_ref.setText(1, str(self.editing_item_ref))

    def add_condition(self):
        if self.selected_index < 0: return
        new_c = {"type": self.c_type.currentData()}
        self.current_triggers[self.selected_index]["conditions"].append(new_c)
        self.on_trigger_selected(self.selected_index)

    def add_action(self):
        if self.selected_index < 0: return
        new_a = {"type": self.a_type.currentData()}
        self.current_triggers[self.selected_index]["actions"].append(new_a)
        self.on_trigger_selected(self.selected_index)

    def delete_condition(self):
        item = self.cond_tree.currentItem()
        if not item: return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = item.parent()
        
        target_list = None
        if parent_item:
            # Inside a logic group
            parent_data = parent_item.data(0, Qt.ItemDataRole.UserRole)
            target_list = parent_data.get("conditions")
        else:
            # Root
            if self.selected_index >= 0:
                target_list = self.current_triggers[self.selected_index]["conditions"]
        
        if target_list is not None and data in target_list:
            target_list.remove(data)
            self.on_trigger_selected(self.selected_index)

    def delete_action(self):
        item = self.act_tree.currentItem()
        if not item or self.selected_index < 0: return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        target_list = self.current_triggers[self.selected_index]["actions"]
        if data in target_list:
            target_list.remove(data)
            self.on_trigger_selected(self.selected_index)

if __name__ == "__main__":
    app = QApplication(sys.argv); ex = TriggerEditor(); ex.show(); sys.exit(app.exec())
