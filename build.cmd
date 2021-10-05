rd/s/q build
rd/s/q dist
pyinstaller QwQ.py -p Cmd.py --hidden-import Cmd
copy "config.yml" dist/QwQ