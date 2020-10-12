##
# Copyright 2020 Charles Y. Choi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

venv:
	python3 -m venv ./venv

install-dependencies: venv
	pip install -r requirements.txt


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

