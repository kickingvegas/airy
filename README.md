# airy

*airy* is a command line Python script to read a [PurpleAir](https://www2.purpleair.com) sensor reading via PurpleAir's REST API. 

## Features

- Command line interface to support automation.
- Storage of _PurpleAir_ sensor readings are stored in [SQLite](https://www.sqlite.org/index.html) 3 database.
- SMS alert support to be notified when AQI has gotten worse or better.
   - Requires [Twilio](https://www.twilio.com) SMS service

## Example

```
$ ./airy.py 60015
Airy SensorID: 60015
    Raw PM2.5: 9.96 ↓ -10.4%
    EPA PM2.5: 41
 AQ & U PM2.5: 43
      Level 0: Good. Air quality is considered satisfactory.
```

## How to use

TBD

## Requirements

TBD


## TL;DR Installation

In the top level directory `airy` execute the following commands:

``` 
$ make venv
$ source venv/bin/activate
$ make install-dependencies
```

## License

Copyright 2020 Charles Y. Choi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.








