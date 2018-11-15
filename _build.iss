;My Installer for the GenerateHeader.py setup

; This was taken from the example page of fileread
#define FileHandle
#sub ProcessFileLine                                                         
  #define public _VERSION FileRead(FileHandle)
#endsub
#for {FileHandle = FileOpen("version.txt"); \
  FileHandle && !FileEof(FileHandle); ""} \
  ProcessFileLine
#if FileHandle
  #expr FileClose(FileHandle)
#endif
#pragma message "Displaying File Version"
#pragma message _VERSION


[Setup]
AppName="Discord DM Helper"
AppVersion={#_VERSION}
DefaultDirName={userdesktop}
DisableProgramGroupPage=yes
Compression=lzma2                                                                             
OutputBaseFilename=DiscordDMHelper_v{#_VERSION}
SolidCompression=yes
Uninstallable=no
OutputDir="release"
SetupIconFile="src\img\icon.ico"
PrivilegesRequired=admin 

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs
; We will ship the version with this file, so we can test on the first running if we need to update
; Source: "version.txt"; DestDir: "{app}"
; We will also ship files for running the VB Audio Driver
Source: "audioCable\*"; DestDir: "{tmp}"

; [Icons]
; Name: "{userdesktop}\DiscordDMHelper"; FileName: "{app}\DiscordDMHelper.exe"; WorkingDir: "{app}"; IconFilename: "{app}\img\icon.ico" 

[Run]
Filename: "{tmp}\VBCABLE_Setup_x64.exe"; Description: "Install Audio Drivers";Flags: runascurrentuser postinstall unchecked