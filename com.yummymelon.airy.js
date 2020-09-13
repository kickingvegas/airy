{
    "StartCalendarInterval" : [
	{ "Minute" : 0 },
	{ "Minute" : 10 },
	{ "Minute" : 20 },
	{ "Minute" : 30 },
	{ "Minute" : 40 },
	{ "Minute" : 50 }		
    ],
    "WorkingDirectory": "/Users/cchoi/Projects/airy",
    "ProgramArguments" : [
	"/opt/local/bin/python3",
	"airy.py",
	"-l",
	"--twilio-sid=ACab5878ba43452d4e77688181c2a60217",
	"--twilio-token=0c2e46ead4c384403e6717ef3b510065",
	"--twilio-number=+13018042251",
	"--to-sms=+14152972054",
	"60015"
    ],
    "Label" : "com.yummymelon.airy",
    "ProcessType": "Standard",
    "RunAtLoad": true,
    "StandardOutPath": "/Users/cchoi/Library/Application Support/airy/airy.stdout",
    "StandardErrorPath": "/Users/cchoi/Library/Application Support/airy/airy.stderr",
    "EnvironmentVariables": {
	"PATH": "/opt/local/bin:/opt/local/sbin:/opt/X11/bin:/usr/bin:/bin:/usr/sbin:/sbin",
	"HOME": "/Users/cchoi"
    }
}
