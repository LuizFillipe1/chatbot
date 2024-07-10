import datetime
import json
import logging

from dynamodb_operations import get_from_dynamodb, save_to_dynamodb
from polly_operations import generate_audio_and_store_in_s3
from utils import generate_unique_id

# Configure o logger para registrar informações e erros
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Função de verificação de saúde da API
def health(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

# Função para descrição da versão da API
def v1_description(event, context):
    body = {
        "message": "TTS api version 1."
    }

    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

# Função para processar a conversão de texto para fala
def process_tts(event, context):
    try:
        # Loga o evento recebido
        logger.info("Received event: %s", event)

        if 'body' in event:
            # Faz o parse do corpo da requisição JSON
            body = json.loads(event['body'])
        else:
            body = {}

        # Loga o corpo da requisição após o parse
        logger.info("Parsed body: %s", body)

        # Obtém a frase da requisição
        phrase = body.get('phrase')

        if not phrase:
            # Retorna um erro se a frase não for fornecida
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Frase não fornecida"
                })
            }

        # Gera um ID único para a frase
        unique_id = generate_unique_id(phrase)
        logger.info("Generated unique_id: %s", unique_id)

        # Verifica se a frase já foi processada anteriormente
        existing_item = get_from_dynamodb(unique_id)
        logger.info("Existing item: %s", existing_item)

        if existing_item:
            # Se a frase já existe, retorna os dados existentes
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "received_phrase": existing_item['received_phrase'],
                    "url_to_audio": existing_item['url_to_audio'],
                    "created_audio": existing_item['created_audio'],
                    "unique_id": unique_id
                }, indent=4)
            }
        else:
            # Gera o áudio e armazena no S3
            audio_url = generate_audio_and_store_in_s3(phrase, unique_id)
            logger.info("Generated audio URL: %s", audio_url)

            # Salva os dados no DynamoDB
            save_to_dynamodb(phrase, unique_id, audio_url)

            # Retorna a resposta com os dados recém-criados
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "received_phrase": phrase,
                    "url_to_audio": audio_url,
                    "created_audio": datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                    "unique_id": unique_id
                }, indent=4)
            }
    except Exception as e:
        # Loga o erro e retorna uma resposta de erro interno
        logger.error("Error processing TTS: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal Server Error",
                "error": str(e)
            })
        }
