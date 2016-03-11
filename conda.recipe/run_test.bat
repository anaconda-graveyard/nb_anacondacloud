"%PREFIX%\Scripts\npm.cmd" install --no-progress --no-spinner && "%PREFIX%\Scripts\npm.cmd" run test  --no-progress --no-spinner && if errorlevel 1 exit 1
