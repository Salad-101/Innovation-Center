; Inno Setup script for Innovation Center.
;
; 1. Install Inno Setup: https://jrsoftware.org/isinfo.php
; 2. Build the PyInstaller app first (see main.spec) so dist\InnovationCenter\
;    exists.
; 3. Open this file in the Inno Setup Compiler (or run ISCC.exe on it) and
;    click Compile. Output goes to packaging\Output\InnovationCenter-Setup.exe

#define MyAppName "Innovation Center"
#define MyAppVersion "1.0.0"
#define MyAppExeName "InnovationCenter.exe"

[Setup]
AppId={{B6C1B2B0-6B7B-4B1D-9B9D-INNOVATIONCENTER}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=InnovationCenter-Setup
Compression=lzma2
SolidCompression=yes
; Per-user install avoids needing admin rights and keeps the install dir
; writable, which is convenient (though main.py already stores the database
; in %LOCALAPPDATA% regardless, so this is just a convenience, not a
; requirement).
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
; Pulls in the ENTIRE onedir build - exe, bundled libraries, and the
; backend/ + frontend/dist data files copied in by main.spec.
Source: "..\dist\InnovationCenter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent
