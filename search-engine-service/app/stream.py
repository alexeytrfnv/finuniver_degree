import asyncio
from faststream import FastStream
from app.streaming.broker import broker

import app.core.qdrant.uploading

stream_app = FastStream(broker)
    
