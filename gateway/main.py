from fastapi import FastAPI, HTTPException , File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import base64
import pika
import os
import rpc_client
import timeit
import hashlib
import redis

def generate_hash_key(file_content):
    return hashlib.sha256(file_content.encode()).hexdigest()


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load environment variables
load_dotenv()
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL))  # add container name in docker
channel = connection.channel()
channel.queue_declare(queue='gateway_service')
channel.queue_declare(queue='blast_service')

# Connect to Redis
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True, socket_timeout=10)
client.flushdb()


@app.get('/', tags=["Welcome"])
def hello_world():
    return {'message': "hello world"}


@app.get('/blast', tags=['Blast Service'])
def blast(user_id: str, outfmt: int = 5, file: UploadFile = File(...)):
    start = timeit.default_timer()
    print(f"Received user_id: {user_id}, outfmt: {outfmt}, file: {file.filename}")

    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())

    blast_rpc = rpc_client.BlastRpcClient()

    with open(file.filename, "rb") as buffer:
        file_data = buffer.read()
        file_base64 = base64.b64encode(file_data).decode()

    hash_key = generate_hash_key(file_base64)

    if client.exists(hash_key):
        print(f"Hash key {hash_key} already exists in Redis.")
        return client.get(hash_key)

    request_json = {
        'user_id': user_id,
        'outfmt': outfmt,
        'file': file_base64
    }

    response = blast_rpc.call(request_json)
    client.set(hash_key, "don't bother me")

    os.remove(file.filename)
    print(f"Done! took {timeit.default_timer() - start}s.")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)