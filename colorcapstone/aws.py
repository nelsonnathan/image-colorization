import boto3
import colorcapstone.key_configuration as keys

s3 = boto3.client('s3', aws_access_key_id=keys.ACCESS_KEY_ID,
                  aws_secret_access_key=keys.ACCESS_SECRET_KEY)

BUCKET_NAME = 'colorization-capstone'