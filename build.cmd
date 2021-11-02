rd/s/q build
rd/s/q dist
pyinstaller win-agent.py -p Cmd.py --hidden-import Cmd -F
copy "config.yml" dist/win-agent