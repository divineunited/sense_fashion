# Sense Fashion

*May 20, 2019*

This fully working web application will allow a user to upload (drag and drop) images that will then be identified - specifically for fashion purposes once the ML model is fully developed and trained. 

----

Tips on Running the App from your Local Server:
If you see this error on AWS S3 - TypeError: expected string or bytes-like object - that means that you are not getting the Bucket and authentication passed to the upload function. So, you need to get the environment variables to be passed to it because our authentication and Bucket is located in our .env files. Make sure you have python-dotenv installed in your environment requirements. To get this uploading to AWS S3, you need to get the Bucket Variables from the .env file. In order to get those authentication variables, you'll need to have a virtual environment called venv set up and installed all the requirements.txt into that virtual environment. Then, you allow the bash to source that venv by typing this in the bash: source venv/Scripts/activate
Afterwards, the .env is setup, and you can type "flask run" to start the server with the proper environment variables passed.

NOTE:
When creating the Docker Image for deployment, a new copy of this was built up from scratch with hard coded environment variables and proper requirements / adjustments made on main.py.


