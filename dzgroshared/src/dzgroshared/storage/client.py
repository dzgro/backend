from sys import prefix
from typing import Union
from botocore.exceptions import ClientError
import boto3
from botocore.config import Config
from dzgroshared.client import DzgroSharedClient
from dzgroshared.functions.DzgroReportsS3Trigger.models import S3TriggerObject
from dzgroshared.models.model import CustomError
from dzgroshared.models.enums import S3Bucket
from dzgroshared.models.s3 import S3PutObjectModel, S3GetObjectModel
from mypy_boto3_s3 import S3Client
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

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
    client: DzgroSharedClient
    s3Client: S3Client

    def __init__(self, client: DzgroSharedClient):
        self.client = client

    def __getattr__(self, item):
        return None

    def getBucketName(self, bucket: S3Bucket):
        return f"{bucket.value}-{self.client.env.value.lower()}"
    
    def getS3TriggerObject(self, data: dict):
        return {'Records': [
            data
        ]}
    
    def getS3Client(self):
        if self.s3Client: return self.s3Client
        from botocore.config import Config
        from typing import cast
        import boto3
        self.s3Client = cast(S3Client, boto3.client('s3', config=Config(region_name=self.client.REGION)))
        return self.s3Client

    @s3_exception_handler
    def put_object(self, req: S3PutObjectModel, Body: Union[str, bytes]):
        obj = req.model_dump(mode="json", exclude_none=True)
        obj['Bucket'] = self.getBucketName(req.Bucket)
        obj['Body'] = Body
        return self.getS3Client().put_object(**obj)

    @s3_exception_handler
    def get_object(self, req: S3GetObjectModel):
        obj = req.model_dump(mode="json", exclude_none=True)
        obj['Bucket'] = self.getBucketName(req.Bucket)
        return self.getS3Client().get_object(**obj)
    
    @s3_exception_handler
    def create_signed_url_by_path(self, path:str, bucket: S3Bucket, ExpiresIn: int = 604800):
        return self.getS3Client().generate_presigned_url('get_object', Params={'Bucket': self.getBucketName(bucket), 'Key': path},ExpiresIn=ExpiresIn)

    @s3_exception_handler
    def list_objects_v2(self, Bucket: S3Bucket, Prefix:str):
        return self.getS3Client().list_objects_v2(Bucket=self.getBucketName(Bucket), Prefix=Prefix)

    @s3_exception_handler
    def delete_objects(self, Bucket: S3Bucket, Keys:list[str]):
        return self.getS3Client().delete_objects(Bucket=self.getBucketName(Bucket), Delete={"Objects":[{'Key': key} for key in Keys]})

    @s3_exception_handler
    def delete_object(self, Bucket: S3Bucket, Key:str):
        return self.getS3Client().delete_object(Bucket=self.getBucketName(Bucket), Key=Key)

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
