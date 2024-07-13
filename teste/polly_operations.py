import boto3
from s3_operations import create_bucket

# Inicializa a sessão boto3 e cria recursos para Polly e S3
session = boto3.Session()
polly = session.client('polly')
s3 = session.client('s3')
region = session.region_name
bucket_name = 'nomeSuaBucket'


create_bucket(bucket_name, region)


# Função para gerar áudio e armazenar no S3
def generate_audio_and_store_in_s3(phrase, unique_id):
    response = polly.synthesize_speech(
        Text=phrase,
        OutputFormat='mp3',
        VoiceId='Camila'
    )

    audio_key = f'audio-{unique_id}.mp3'
    s3.put_object(Bucket=bucket_name, Key=audio_key, Body=response['AudioStream'].read())

    return f'https://{bucket_name}.s3.amazonaws.com/{audio_key}'
