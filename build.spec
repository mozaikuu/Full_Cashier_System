from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project = Path(SPECPATH)
a = Analysis([str(project / "main.py")], pathex=[str(project)], hiddenimports=collect_submodules("sqlalchemy"), datas=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, exclude_binaries=True, name="MoussaCashier", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="MoussaCashier")
