import yaml
import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BilibiliConfig:
    sessdata: str
    bili_jct: str
    dedeuserid: str

@dataclass
class ChannelConfig:
    url: str
    name: str
    bilibili_tag: str
    bilibili_tid: int

@dataclass
class AppConfig:
    check_interval: int
    download_path: str
    fetch_limit: int = 5
    proxy: Optional[str] = None

class Config:
    def __init__(self, config_path: str = "config/config.yaml"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}. Please copy config.yaml.example to config.yaml and fill it in.")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        self.app = AppConfig(**data.get('app', {}))
        self.bilibili = BilibiliConfig(**data.get('bilibili', {}))
        self.youtube_channels = [ChannelConfig(**c) for c in data.get('youtube', {}).get('channels', [])]

# Global config instance
_config_instance = None

def load_config(path: str = "config/config.yaml") -> Config:
    global _config_instance
    _config_instance = Config(path)
    return _config_instance

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        return load_config()
    return _config_instance
