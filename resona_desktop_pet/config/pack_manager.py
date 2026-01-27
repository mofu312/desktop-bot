import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
class PackManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.packs_dir = project_root / "packs"
        self.active_pack_id = "Resona_Default"
        self.pack_data: Dict[str, Any] = {}
        self.id_map: Dict[str, str] = {}
        self._scan_packs()
    def _scan_packs(self):
        self.id_map = {}
        if not self.packs_dir.exists(): return
        for p_dir in self.packs_dir.iterdir():
            if p_dir.is_dir():
                manifest = p_dir / "pack.json"
                if manifest.exists():
                    try:
                        with open(manifest, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            pid = data.get("pack_info", {}).get("id")
                            if pid:
                                self.id_map[pid] = p_dir.name
                    except: pass
    def set_active_pack(self, pack_id: str):
        folder_name = self.id_map.get(pack_id, pack_id)
        self.active_pack_id = folder_name
        self._load_pack_manifest()
    def _load_pack_manifest(self):
        manifest_path = self.packs_dir / self.active_pack_id / "pack.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    self.pack_data = json.load(f)
            except Exception as e:
                print(f"[PackManager] Error loading manifest: {e}")
        else:
            print(f"[PackManager] Manifest not found: {manifest_path}")
    def get_info(self, key: str, default: Any = None) -> Any:
        if not self.pack_data:
            self._load_pack_manifest()
        return self.pack_data.get(key, default)
    def get_path(self, category: str, key: str = None) -> Optional[Path]:
        if not self.pack_data:
            self._load_pack_manifest()
        pack_root = self.packs_dir / self.active_pack_id
        try:
            rel_path = None
            if category == "logic":
                if key == "triggers": rel_path = self.pack_data["logic"]["interaction_configs"].get("triggers")
                elif key == "prompts": 
                    prompts = self.pack_data["logic"].get("prompts", [])
                    if prompts: rel_path = prompts[0].get("path")
                elif key == "error_config": rel_path = self.pack_data["logic"]["interaction_configs"].get("error_config")
                elif key == "emotions": rel_path = self.pack_data["logic"]["interaction_configs"].get("emotions")
                elif key == "thinking": rel_path = self.pack_data["logic"]["interaction_configs"].get("thinking")
                elif key == "listening": rel_path = self.pack_data["logic"]["interaction_configs"].get("listening")
            elif category == "audio":
                if key == "event_dir": rel_path = self.pack_data["audio"]["event_audio_dir"]
                elif key == "emotion_dir": rel_path = self.pack_data["audio"]["emotion_audio_dir"]
                elif key == "error_dir": rel_path = self.pack_data["audio"]["error_audio_dir"]
            elif category == "model":
                rel_path = self.pack_data["character"]["sovits_model"].get(key)
            if rel_path:
                p = Path(rel_path)
                if p.is_absolute(): return p
                return pack_root / rel_path
        except Exception as e:
            print(f"[PackManager] Error resolving path for {category}:{key} - {e}")
        return None
    def get_character_name(self) -> str:
        return self.pack_data.get("character", {}).get("name", "Unknown")
    def get_available_packs(self) -> list:
        if not self.packs_dir.exists(): return []
        return [d.name for d in self.packs_dir.iterdir() if d.is_dir() and (d / "pack.json").exists()]