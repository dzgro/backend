from botocore.exceptions import ClientError
import boto3
from botocore.config import Config
from models.model import CustomError
from storage.model import S3PutObjectModel, S3GetObjectModel, S3Bucket

my_config = Config(
    region_name = 'ap-south-1'
)
s3 = boto3.client('s3', config=my_config)
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError, EndpointConnectionError

def s3_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except NoCredentialsError:
            raise CustomError({"error": "AWS credentials not found. Please configure them."})
        
        except EndpointConnectionError as e:
            raise CustomError({"error": f"Could not connect to the endpoint"})
        
        except ClientError as e:
            error = e.response.get("Error", {})
            code = error.get("Code", "UnknownClientError")
            message = error.get("Message", str(e))
            raise CustomError({"error" :message})

        except Exception as e:
            raise ValueError(f"An unexpected error occurred")
    return wrapper


class S3Storage:

    def __init__(self):
        pass

    @s3_exception_handler
    def put_object(self, req: S3PutObjectModel):
        return s3.put_object(**req.model_dump(mode="json", exclude_none=True))

    @s3_exception_handler
    def get_object(self, req: S3GetObjectModel):
        return s3.get_object(**req.model_dump(mode="json", exclude_none=True))
    
    # def uploadPilImage(self, image, path: str):
    #     in_mem_file = BytesIO()
    #     image.save(in_mem_file, format=image.format, quality=100)
    #     in_mem_file.seek(0)
    #     self.put_object(in_mem_file, path, 'image/jpg')
    #     in_mem_file.close()

    # def delete_folder(self, folder_path):
    #     s3_data = self.list_objects_by_path(folder_path)
    #     contents = s3_data['Contents'] if 'Contents' in s3_data else []
    #     while len(contents) != 0:
    #         for obj in contents:
    #             key = obj.get('Key')
    #             if key: self.delete_object(key)
    #         s3_data = self.list_objects_by_path(folder_path)
    #         contents = s3_data['Contents'] if 'Contents' in s3_data else []

    # def delete_object(self, key):
    #     try:
    #         s3.delete_object(Bucket=self.bucket, Key=key)
    #         return True
    #     except ClientError as ex:
    #         raise ValueError('Object Could not deleted')
    #     except:
    #         raise ValueError('Internal Error Occurred')

    
    # def getObjectHeaders(self, path: str):
    #     response = s3.head_object(Bucket=self.bucket, Key=path)
    #     return response

    # def list_objects_by_path(self, path, continuation_token:str|None=None):
    #     try:
    #         if continuation_token: return s3.list_objects_v2(Bucket=self.bucket, Prefix=path, ContinuationToken=continuation_token)
    #         return s3.list_objects_v2(Bucket=self.bucket, Prefix=path)
    #     except ClientError as ex:
    #         raise ValueError('Objects cannot be listed for this path')
    #     except:
    #         raise ValueError('Internal Error Occurred')
    @s3_exception_handler
    def create_signed_url_by_path(self, path:str, bucket: S3Bucket=S3Bucket.DZGRO):
        return s3.generate_presigned_url('get_object', Params={'Bucket': bucket.value, 'Key': path},ExpiresIn=604800)

    # def get_object(self, path):
    #     try:
    #         obj = s3.get_object(Bucket=self.bucket, Key=path)
    #         return obj['Body'].read()
    #     except ClientError as ex:
    #         print(ex.args)
    #         raise ValueError('Object Could not be found')
    #     except:
    #         raise ValueError('Internal Error Occurred')

    # def get_object_as_buffer(self, path):
    #     try:
    #         obj = s3.get_object(Bucket=self.bucket, Key=path)
    #         return obj['Body']
    #     except ClientError as ex:
    #         raise ValueError('Object Could not be found')
    #     except:
    #         raise ValueError('Internal Error Occurred')

    # def get_object_with_mime_type(self, path) -> dict:
    #     try:
    #         obj = s3.get_object(Bucket=self.bucket, Key=path)
    #         mime_type = obj['ContentType']
    #         return {"body": obj['Body'].read(), "mime_type": mime_type, "length": obj['ContentLength']}
    #     except ClientError as ex:
    #         raise ValueError('Object Could not be found')
    #     except:
    #         raise ValueError('Internal Error Occurred')

    # def generate_upload_link(self, path:str, mime_type: str|None = None):
    #     try:
    #         conditions = [["eq", "$Content-Type", mime_type]] if mime_type is not None else None
    #         fields = {'Content-Type': mime_type} if mime_type is not None else None
    #         return s3.generate_presigned_post(
    #             self.bucket,
    #             Key=path,
    #             Fields=fields,
    #             Conditions=conditions,
    #             ExpiresIn=3600,
    #         )
    #     except ClientError as ex:
    #         raise ValueError('Url not Generated')
    #     except:
    #         raise ValueError('Internal Error Occurred')
        
    # def copyFile(self, source:str, destination: str, sourceBucket: PredefinedBuckets|None=None):
    #     try:
    #         bucket = sourceBucket if sourceBucket else self.bucket
    #         s3.copy_object(Bucket=self.bucket, CopySource=bucket+'/'+source, Key=destination)
    #     except ClientError as ex:
    #         raise ValueError('Url not Generated')
    #     except:
    #         raise ValueError('Internal Error Occurred')
        
    # def changeContentType(self, key:str, contentType:str):
    #     s3.copy_object(Key=key, Bucket=self.bucket,
    #                       CopySource={"Bucket": self.bucket, "Key": key},
    #                       ContentType=contentType,
    #                       MetadataDirective="REPLACE")
