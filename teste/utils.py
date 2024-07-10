import hashlib


# Função para gerar um ID único para a frase
def generate_unique_id(phrase):
    hash_object = hashlib.sha256(phrase.encode())
    return hash_object.hexdigest()[:6]
