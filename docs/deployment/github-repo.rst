Git Client and Github Repository
================================

Heroku is closely integrated with the git source code version control system, using it to upload/synchronise any changes you make to the live system. It does this by adding a new heroku "remote" repository named heroku pointing to a repository for your source on the Heroku cloud. During development you use git to store changes on your own repository. When you want to deploy your site, you sync your changes to the Heroku repository.

Note: If you're used to following good software development practices you are probably already using git or some other SCM system. If you already have a git repository, then you can skip this step.

There are a lot of ways to work with git, but one of the easiest is to first set up an account on Github, create the repository there, and then sync to it locally:

Install git client
------------------

1. Install git by downloading the relevant excutable from https://git-scm.com/downloads.
2. Check the installation by typing ``git`` or ``git help`` in Command Prompt. 
3. Open Command Prompt/terminal and clone a git repository by searching the github wesbite (https://github.com) by typing like this. 

.. parsed-literal::
	git clone https://github.com/<your_git_user_id>/<project_name>.git
	cd <project_name>


Creating an application repository in Github
--------------------------------------------

Create a github account
***********************

1. Visit https://github.com/ and create an account.
2. Once you are logged in, click the + link in the top toolbar and select New repository.
3. Fill in all the fields on this form. While these are not compulsory, they are strongly recommended.
4. Enter a new repository name (e.g. staffcalibration), and description (e.g. "Staff Calibration website written in Django".
5. Choose Python in the Add .gitignore selection list.
6. Choose your preferred license in the Add license selection list.
7. Check Initialize this repository with a README.
8. Press Create repository.
9. Click the green "Clone or download" button on your new repo page.
10. Copy the URL value from the text field inside the dialog box that appears (it should be something like: https://github.com/<your_git_user_id>/staff_calibration.git).

Now that the repository ("repo") is created we are going to want to clone it on our local computer:

Synchronising the github repository
***********************************

1. Copy your Django application into the git folder (all the files at the same level as manage.py and below, not their containing staff_calibration folder).
2. Open the .gitignore file, copy the following lines into the bottom of it, and then save (this file is used to identify files that should not be uploaded to git by default):

.. code:: python

	.venv/                  # virtual environment 	               
	*.bak                   # Text backup files
	*.sqlite3               # Database

3. Open a command prompt/terminal and navigate to your github project directory. Use the add command to add all files to git. This adds the files which aren't ignored by the .gitignore file to the "staging area"

.. parsed-literal::
	git add -A

4. Use the status command to check that all files you are about to commit are correct (you want to include source files, not binaries, temporary files etc.). It should look a bit like the listing below.

.. parsed-literal::
	git status 
		Your branch is up-to-date with 'origin/main'.
		Changes to be committed:
		(use "git reset HEAD <file>..." to unstage)
		     modified:   .gitignore
		     new file:   catalog/__init__.py
		     ...
		     new file:   catalog/migrations/0001_initial.py
		     ...
		     new file:   templates/registration/password_reset_form.html
		On branch main
		
5. After that commit the files to your local repository. This is essentially equivalent to signing off on the changes and making them an official part of the local repository.

.. parsed-literal::
	git commit -m "First version of application moved into github"

6. At this point, the remote repository has not been changed. Synchronise (push) your local repository to the remote Github repository using the following command:

.. parsed-literal::
	git push origin main

When this operation completes, the git respository is updated in the Github page with all the files. Update the respository by issuing the add/commit/push commands every time a change is made in the local project directory. It is also possible to connect deploy Heroku application using the Github repository.

