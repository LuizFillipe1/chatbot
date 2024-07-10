import boto3
from botocore.exceptions import ClientError


# Verifica se já existe a bucket
def check_bucket_exists(bucket_name):
    s3_client = boto3.client('s3')
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False
    

# Criação da bucket 
def create_bucket(bucket_name, region=None):
    try:
        if check_bucket_exists(bucket_name):
            print("Bucket já existente")
            return False

        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)

        else:
            s3_client = boto3.client('s3', region_name=region)
            s3_client.create_bucket(Bucket=bucket_name)
        print(f'Bucket {bucket_name} criado com sucesso!')
        return True
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f'Você já possui o bucket "{bucket_name}".')
        elif error_code == 'BucketAlreadyExists':
            print(f'O nome do bucket "{bucket_name}" já está em uso globalmente. Tente um nome diferente.')
        else:
            print(f'Erro ao criar o bucket: {e}')
        return False
