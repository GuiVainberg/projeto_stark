import time
from datetime import datetime

import schedule
from invoice_factory import generate_random_invoices

CYCLES = 8
INTERVAL_HOURS = 3

counter = {"runs": 0}

def run_cycle():
    counter["runs"] += 1
    print(f"[{datetime.now().astimezone()}] Run {counter['runs']}/{CYCLES}")
    generate_random_invoices()
    if counter["runs"] >= CYCLES:
        print("24h run completed.")
        return schedule.CancelJob

if __name__ == "__main__":
    run_cycle()  # first run happens immediately
    schedule.every(INTERVAL_HOURS).hours.do(run_cycle)
    while True:
        schedule.run_pending()
        time.sleep(30)