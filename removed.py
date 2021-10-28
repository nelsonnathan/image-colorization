#from routes.py - code to generate a presigned url
# img_url = s3.generate_presigned_url(
            #     ClientMethod='get_object',
            #     Params={
            #         'Bucket': BUCKET_NAME,
            #         'Key': filename
            #     }
            # )



#from routes.py - can't remember what i was doing with this. it was in the upload() function, beneath the filename variable declaration
# bucket_location = boto3.client(
            #     's3').get_bucket_location(Bucket=BUCKET_NAME)