# trip-data-crawler

## dependency

```bash
pip install -r requirements.txt
```

## proxy pool

### redis

```bash
docker run -p 6379:6379 --name redis-pool -d redis
```

### proxy pool

```bash
docker run --env DB_CONN=redis://<ip:port>/0 -p 5010:5010 jhao104/proxy_pool
```