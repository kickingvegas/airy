
com.yummymelon.airy.plist: com.yummymelon.airy.js
	plutil -convert xml1 -o com.yummymelon.airy.plist com.yummymelon.airy.js

install-plist: ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist: com.yummymelon.airy.plist
	cp com.yummymelon.airy.plist ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

start-daemon: ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist
	launchctl load ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

stop-daemon: 
	launchctl unload ${HOME}/Library/LaunchAgents/com.yummymelon.airy.plist

