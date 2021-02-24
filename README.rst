### Overview

This is a django-based web application developed by Landgate for itself and other external users (e.g., surveyors and engineers) who are engaged in measuring absolute or relative height differences on the ground, to easily calibrate their levelling staves online and apply the calibration parameters instantly to their measurements. However, users must note that staff calibration is a binary process and involves the Staff Calibration Range located at Boya - (1) Landgate monitors the Boya Range constantly using calibrated invar staves and updates the range records, and (2) users calibrate their levelling staves by measuring the Boya Range and processing their readings through this web application.    

This application replaces the existing 'staff' software (executable written in Delphi) provided by Landgate. Written in python, html, css and some javascripts, this new application:

* is mathematically more robust by considering the signifcant seasonal variation in range,
* users have more control over how they manage their staff calibration records, and
* has the ability to do both range and staff calibrations, which is very important to Landgate for monitoring the Boya Staff Calibration Range, 

### Requirements

Python 3.8 or higher plus see requirements.txt

### Installation

Download the ```staff``` package from the github and unzip to your working directory. 

Install ```Python 3``` or ```Anaconda 3```. Note that this application has been tested with ```Python 3.8.3```

Install the python packages from the requirements.txt from the Command Prompt:

``` pip install -r requirements.txt```

In your Command Prompt, go to the working directory and type the following:

```	
	cd staff

	virtual venv

	.\venv\Script\activate

	pip install -r requirements.txt

	python manage.py makemigrations

	python manage.py migrate
```

Type the email address and password when prompted. If migration is successful, type:

```

	python manage.py runserver

```

Open the internet browser and copy the development server address to view the website. More information is provided under docs/_build/html

### Authors

* **Irek Baran**, *Project Management*, Landgate
* **Tony Castelli** - *Testing, Feedback, and Data Aquisition*, Landgate
* **Vanessa Ung** - *Testing, Feedback, and Data Aquisition*, Landgate
* **Brendon Helmund** - *Testing, Feedback, and Data Aquisition*, Landgate
* **Rod Stone** - *Testing and Feedback*, Main Roads Western Australia
* **Linda Morgan** - *Testing and Feedback*
* **Kent Wheeler** - *Testing and Feedback*, Landgate
* **Khandu** - *Software, Testing, Integration and Deployment*, Landgate


### License

Copyright 2020-2021 Landgate

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

>>>>>>> ce46ce4715147a9b071e0c4a5372dd27f196603e
