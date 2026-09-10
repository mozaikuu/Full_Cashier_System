# Windows build

Build on Windows, using the same Python version as the client machine.

1. Open PowerShell in the project folder.
2. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build.ps1
```

3. Give the client the complete `dist\SandyCashier` folder. The executable is `SandyCashier.exe`.
4. Do not give only the `.exe`; the onedir build needs the files beside it.
5. On the client PC, launch `SandyCashier.exe`. The database is created in the app's `data` folder.

For a clean client test, copy the `dist\SandyCashier` folder to a Windows machine without Python and launch the executable there.

The first login password is `1234`. The recovery code is `SANDY-RESET`.