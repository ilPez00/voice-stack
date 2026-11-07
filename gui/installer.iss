[Setup]
AppName=voice-stack GUI
AppVersion=1.0
DefaultDirName={autopf}\voice-stack
DefaultGroupName=voice-stack
OutputDir=installer
OutputBaseFilename=voice-stack-setup
Compression=lzma
SolidCompression=yes
LicenseFile=..\LICENSE

[Files]
Source: "..\dist\voice-stack-gui\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\voice-stack"; Filename: "{app}\voice-stack-gui.exe"
Name: "{commondesktop}\voice-stack"; Filename: "{app}\voice-stack-gui.exe"

[Run]
Filename: "{app}\voice-stack-gui.exe"; Description: "Launch voice-stack"; Flags: nowait postinstall skipifsilent
