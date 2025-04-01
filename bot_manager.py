import multiprocessing
import asyncio
from bot import main  

def run_bot():
    asyncio.run(main())  

if __name__ == "__main__":
    process_count = 3 
    processes = []

    for _ in range(process_count):
        p = multiprocessing.Process(target=run_bot)  
        p.start()
        processes.append(p)

    for p in processes:
        p.join()  
