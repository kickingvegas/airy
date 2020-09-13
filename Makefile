LOG_DIR="${HOME}/Library/Application Support/airy"
LOG_STDOUT=${LOG_DIR}/airy.stdout
LOG_STDERR=${LOG_DIR}/airy.stderr

go:
	./airy.py 60015

log:
	tail -n 20 ${LOG_STDOUT} | grep -e '^20'

err:
	tail -n 20 ${LOG_STDERR}

help:
	./airy.py -h

com.yummymelon.airy.plist: com.yummymelon.airy.js
	plutil -convert xml1 -o com.yummymelon.airy.plist com.yummymelon.airy.js

install-plist: ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist: com.yummymelon.airy.plist
	cp com.yummymelon.airy.plist ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

start-daemon: ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist
	launchctl load ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

stop-daemon: 
	launchctl unload ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

status:
	launchctl list | grep airy

clean:
	find . -name '*~' -exec rm {} \;
	find . -name '*.*~' -exec rm {} \;
	- rm com.yummymelon.airy.plist

