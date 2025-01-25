from celery import shared_task
import time


@shared_task(ignore_result=False)
def hello_world():
    for i in range(1, 6):
        print(i)
        time.sleep(1)
    print("Hello Celery")


@shared_task(ignore_result=False)
def fetch_and_process_sales_data():
    print("Fetching and processing sales data")
