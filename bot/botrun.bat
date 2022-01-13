@echo off

call %~dp0phytonProject\venv\Scripts\activate

cd %~dp0phytonProject\bot

set TOKEN=OTMwODc4MjkwNTIzMjA1NzQz.Yd8R9w.oR4f-nIRXa3fw1irFy61q3jwF-M

python PBot.py

pause