"%PREFIX%\node_modules\npm\npm.cmd" install . --no-spin --no-progress && "%PREFIX%\node_modules\npm\npm.cmd" run test --no-progress --no-spin && if errorlevel 1 exit 1
