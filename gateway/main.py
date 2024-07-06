from fastapi import FastAPI, HTTPException, File, UploadFile, APIRouter
from dotenv import load_dotenv
import base64
import pika
import os
import rpc_client
import timeit
import hashlib
import redis
import json
import logging
from datetime import datetime


class Blast:
    def __init__(self):
        self.client = self._init_redis()
        self.channel = self._init_rabbitmq()
        self.cache_storage = "cache_storage"
        self.router = APIRouter()
        self.router.add_api_route("/blast", self.blast, methods=["GET"])


    def _init_redis(self):
        REDIS_URL = os.environ.get("REDIS_URL")
        REDIS_PORT = os.environ.get("REDIS_PORT")
        client = redis.StrictRedis(host=REDIS_URL, port=REDIS_PORT, db=0, decode_responses=True, socket_timeout=10)
        client.flushdb()

        return client

    def _init_rabbitmq(self):
        # Connect to RabbitMQ
        RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue="gateway_service")
        channel.queue_declare(queue="blast_service")

        return channel

    def check_cache(self, hash_key):
        if self.client.exists(hash_key):
            logger.info(f"Hash key {hash_key} hit in Redis!")
            cached_data = self.client.get(hash_key)
            if os.path.exists(cached_data):
                with open(cached_data, "r") as f:
                    data = json.load(f)

                return data
            else:
                logger.warning("But cache file does not exist!")
        else:
            logger.info(f"Hash key doesn't exist")
        return ""


    def cache_data(self, hash_key, data, file_name):
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        cache_file_name = f"{timestamp}_{"".join(file_name.split(".")[:-1])}.json"

        cache_file_dir = os.path.join(self.cache_storage, cache_file_name)

        with open(cache_file_dir, "w") as wf:
            wf.write(json.dumps(data))

        logger.info(f"cache data to {cache_file_dir}")

        self.client.set(hash_key, cache_file_dir)


    def blast(self, user_id: str, outfmt: int = 5, file: UploadFile = File(...)):
        start = timeit.default_timer()
        file_name = file.filename
        logger.info(f"Received user_id: {user_id}, outfmt: {outfmt}, file_name: {file_name}")

        with open(file_name, "wb") as buffer:
            buffer.write(file.file.read())

        blast_rpc = rpc_client.BlastRpcClient()

        with open(file_name, "rb") as buffer:
            file_data = buffer.read()
            file_base64 = base64.b64encode(file_data).decode()

        hash_key = hashlib.sha256(file_base64.encode()).hexdigest()

        if not (response:=self.check_cache(hash_key)):
            request_json = {"user_id": user_id, "outfmt": outfmt, "file": file_base64}

            response = blast_rpc.call(request_json)

            self.cache_data(hash_key, response, file_name)

            os.remove(file.filename)

        logger.info(f"Done! took {timeit.default_timer() - start}s.")
          
        return response

# Load environment variables
load_dotenv()
app = FastAPI()
blast_router = Blast().router
app.include_router(blast_router)
logger = logging.getLogger("uvicorn")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
