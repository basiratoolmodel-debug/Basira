[Setup]
AppName=Basira
AppVersion=1.0.0
AppPublisher=Basira
DefaultDirName={autopf}\Basira
DefaultGroupName=Basira
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=BasiraSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\Basira.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\Basira\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Basira"; Filename: "{app}\Basira.exe"
Name: "{autodesktop}\Basira"; Filename: "{app}\Basira.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Basira.exe"; Description: "Launch Basira now"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{userappdata}\Basira"
Name: "{userdocs}\BasiraData"

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel1.Caption := 'Welcome to the Basira Setup Wizard';
  WizardForm.WelcomeLabel2.Caption := 'This installer will install Basira on your computer.';
end;