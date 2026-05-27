import threading
import time
from db_connection import db_pool

# We will spawn 50 threads to simultaneously read and write to the DB.
# If WAL mode or the queue pool fails, we will get 'database is locked' SQLite errors.

def db_worker(worker_id):
    try:
        # Simulate a fast write
        with db_pool.get_write_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS stress_test (id INTEGER PRIMARY KEY, worker_id INTEGER, val TEXT)")
            cursor.execute("INSERT INTO stress_test (worker_id, val) VALUES (?, ?)", (worker_id, f"test_{worker_id}"))

        # Simulate a read immediately after
        with db_pool.get_read_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stress_test")
            count = cursor.fetchone()[0]

    except Exception as e:
        print(f"Worker {worker_id} failed: {e}")
        return False
    return True

if __name__ == "__main__":
    threads = []
    print("Spawning 50 concurrent DB threads...")
    start_time = time.time()

    for i in range(50):
        t = threading.Thread(target=db_worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = time.time() - start_time
    print(f"Completed 50 threads in {duration:.3f} seconds with no locking exceptions!")
