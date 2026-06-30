from __future__ import annotations

from pathlib import Path

from .base import BaseScanner
from .models import MatchCategory


class SingleFileYamlScanner(BaseScanner):
    filename = ""

    def candidate_files(self, config_dir: Path) -> list[Path]:
        path = config_dir / self.filename
        return [path] if path.is_file() else []


class AutomationScanner(SingleFileYamlScanner):
    name = "automation_scanner"
    category = MatchCategory.AUTOMATION.value
    filename = "automations.yaml"


class ScriptScanner(SingleFileYamlScanner):
    name = "script_scanner"
    category = MatchCategory.SCRIPT.value
    filename = "scripts.yaml"


class SceneScanner(SingleFileYamlScanner):
    name = "scene_scanner"
    category = MatchCategory.SCENE.value
    filename = "scenes.yaml"


class GroupScanner(SingleFileYamlScanner):
    name = "group_scanner"
    category = MatchCategory.GROUP.value
    filename = "groups.yaml"


class ConfigurationScanner(SingleFileYamlScanner):
    name = "configuration_scanner"
    category = MatchCategory.CONFIGURATION.value
    filename = "configuration.yaml"


class TemplateScanner(BaseScanner):
    name = "template_scanner"
    category = MatchCategory.TEMPLATE.value

    def candidate_files(self, config_dir: Path) -> list[Path]:
        candidates: list[Path] = []
        for name in ("templates.yaml", "sensors.yaml", "binary_sensors.yaml"):
            path = config_dir / name
            if path.is_file():
                candidates.append(path)
        for folder in ("templates", "packages"):
            path = config_dir / folder
            if path.is_dir():
                candidates.extend(p for p in path.rglob("*") if p.is_file() and p.suffix in {".yaml", ".yml"})
        return candidates
