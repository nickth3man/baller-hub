## Sync/Async Mismatch in Lifespan
- Encountered a TypeError because 'init_db' was converted to sync but was still being awaited in 'app/main.py' lifespan. Fixed by removing the 'await'.
