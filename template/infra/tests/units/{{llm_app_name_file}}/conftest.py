# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import importlib.util
import os
import sys
import types
from pathlib import Path

os.environ.setdefault("PULUMI_STACK_CONTEXT", "unittest")

_project_root = Path(__file__).parent.parent.parent.parent  # .rendered/infra/

# ---- Package stubs for configurations.<app> --------------------------------
# configurations/llm/ has no __init__.py, so we register fake namespace
# packages so `import configurations.llm.gateway_direct` finds the files
# via their __path__ without needing physical __init__.py files on disk.

_configs_base = _project_root / "configurations"
_app_dirs = sorted(d for d in _configs_base.iterdir() if d.is_dir())
_app_dir = _app_dirs[0]  # one app per project
_app_name = _app_dir.name  # e.g. "llm"

_configs_pkg = types.ModuleType("configurations")
_configs_pkg.__path__ = [str(_configs_base)]  # type: ignore[attr-defined]
_configs_pkg.__package__ = "configurations"
sys.modules.setdefault("configurations", _configs_pkg)

_app_pkg_name = f"configurations.{_app_name}"
_app_pkg = types.ModuleType(_app_pkg_name)
_app_pkg.__path__ = [str(_app_dir)]  # type: ignore[attr-defined]
_app_pkg.__package__ = _app_pkg_name
sys.modules.setdefault(_app_pkg_name, _app_pkg)

# ---- Alias lib<app>.py as configurations.<app>.lib<app> --------------------
# gateway_direct.py uses `from .libllm import ...`.  The actual libllm.py
# lives in infra/, not configurations/llm/, so we load it under the dotted
# name the relative import expects, avoiding any physical file duplication.

_lib_name = f"lib{_app_name}"
_lib_full_name = f"{_app_pkg_name}.{_lib_name}"
_lib_path = _project_root / "infra" / f"{_lib_name}.py"

if _lib_full_name not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_lib_full_name, _lib_path)
    _lib_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
    sys.modules[_lib_full_name] = _lib_mod
    _spec.loader.exec_module(_lib_mod)  # type: ignore[union-attr]
