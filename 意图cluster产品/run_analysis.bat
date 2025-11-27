@echo off
REM Windows批处理脚本 - 快速启动自动化分析

cd /d "%~dp0"
python automated_analysis.py
pause

