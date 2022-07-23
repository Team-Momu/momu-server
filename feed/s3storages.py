import boto3
import uuid

from momu.settings import AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


class S3Client:
    def __init__(self, access_key, secret_key, bucket_name):
        self.s3client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self.bucket_name = bucket_name

    def upload(self, file):
        try:
            file_id = str(uuid.uuid4())
            final_path = 'comments/' + file_id
            self.s3client.upload_fileobj(
                file,
                self.bucket_name,
                final_path,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )
            return f'https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{final_path}'
        except:
            return None


s3client = S3Client(AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME)
