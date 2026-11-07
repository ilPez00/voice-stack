# GUI

Run locally:
- Linux/macOS: `python gui/app.py`
- Windows: `gui\run.bat`

Build:
- Windows: `gui\build_windows.bat`
- Linux: `bash gui/build_linux.sh`

Sign (Windows, requires SDK + PFX):
- `gui\sign_windows.bat dist\<app>\<app>.exe <subject> <cert.pfx> <password>`

Dependencies: Python 3.10+ and stdlib tkinter. ML/audio deps are project-specific and not bundled by this GUI.

## Self-signed cert (dev only)
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=Dev"
openssl pkcs12 -export -out codesign.pfx -inkey key.pem -in cert.pem -passout pass:devpass
