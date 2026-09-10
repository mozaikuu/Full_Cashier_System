# Windows build

Build on Windows, using the same Python version as the client machine.

1. Open PowerShell in the project folder.
2. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build.ps1
```

3. Give the client the complete `dist\MoussaCashier` folder. The executable is `MoussaCashier.exe`.
4. Do not give only the `.exe`; the onedir build needs the files beside it.
5. On the client PC, launch `MoussaCashier.exe`. The database is created in the app's `data` folder.

For a clean client test, copy the `dist\MoussaCashier` folder to a Windows machine without Python and launch the executable there.

The first login password is `1234`. The recovery code is `MOUSSA-RESET`.