@echo off
echo " > Verifying Dependencies."
echo.
timeout /t 3 /nobreak
pip install -r requirements.txt
echo.
echo " > All Dependencies Installed."
echo.
echo " > Starting Webserver. COPY PASTE THE WEB ADDRESS IN THE LAST LINE TO A BROWSER WINDOW."
echo.
pause
python app.py
