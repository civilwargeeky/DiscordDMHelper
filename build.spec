# -*- mode: python -*-

import distutils.sysconfig, os.path
site_packages = distutils.sysconfig.get_python_lib()
def get(*loc):
  return os.path.join(site_packages, *loc)

block_cipher = None


a = Analysis(['main.py'],
             pathex=['Q:\\Coding\\Projects\\Python\\DiscordDMHelper'],
             binaries=[(get("portaudio_x64.dll"), "."), (get("discord", "bin","*"), ".")],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DiscordDMHelper',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
