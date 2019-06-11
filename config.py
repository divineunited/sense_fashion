import os

# this gets the authentication keys from .env file - to have it run correctly, after you set up the .env variable, in the shell, run the command 'flask run'

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")


# # To use Boto 3, you must first import it and tell it what service you are going to use:
# import boto3

# # Let's use Amazon S3
# s3 = boto3.resource('s3')

# # Now that you have an s3 resource, you can make requests and process responses from the service. The following uses the buckets collection to print out all bucket names:
# for bucket in s3.buckets.all():
#     print(bucket.name)