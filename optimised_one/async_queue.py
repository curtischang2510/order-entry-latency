import asyncio
import logging

from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OrderJob:
    coin: str
    size: float
    price: float
    result: asyncio.Future
    
class AsyncOrderQueue:
    def __init__(self, exchange):
        self.queue:asyncio.Queue[OrderJob] = asyncio.Queue()
        self.num_workers = 2
        self.exchange = exchange
        self.worker_task = [
            asyncio.create_task(self._worker(), name=f'order-worker-{i}')
            for i in range(self.num_workers)
        ]

    async def append(self, job: OrderJob):
        await self.queue.put(job)

    async def _worker(self):
        while True:
            job = await self.queue.get()
            try:
                response = await asyncio.to_thread(
                    self.exchange.order,
                    job.coin,
                    True,
                    job.size,
                    job.price,
                    {"limit": {"tif": "Gtc"}},
                )
                job.result.set_result(response)
                logger.info("Order result for %s: %s", job.coin, response)
            except Exception as e:
                job.result.set_exception(e)
                logger.exception("Order failed for %s", job.coin)
            finally:
                self.queue.task_done()
                
    async def join(self):
        await self.queue.join()
