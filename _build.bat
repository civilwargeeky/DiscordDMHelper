python _build_prep.py https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip
pyinstaller _build.spec
"C:\Program Files (x86)\Inno Setup 5\Compil32.exe" /cc _build.iss
python _build_prep.py post
pause