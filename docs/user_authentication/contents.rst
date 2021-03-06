User authentication and permissions
===================================

Staff calibration is a django-based web application designed for Landgate and other external users such as surveyors and engineers who are engaged in measuring absolute or relative height differences on the ground, to calibrate levelling staves online and get the reports instantly. 

To acheive that Django provides an authentication and authorization ("permission") system that allows users to sign up, log in and customize actions specific to them. The Django framework also has built-in models for **Users** and **Groups** to apply permissions to a group of users.

For the Staff Calibration application, users will be asked to **sign up** and **log in** with their emails to add records or calibrate their staves and print calibration recrods. A custom user (**CustomUser**) model is created to manage the users and two groups (**Landgate** and **Others**) are created to allow two permission modes. Landgate users or more specfically the Survey Services are able to do range calibration, which is different from calibrating a staff. 


.. toctree::
   :maxdepth: 4

   1_user_model
   2_forms
   3_authentication_views
   4_password_validation
   5_pre_load





   
