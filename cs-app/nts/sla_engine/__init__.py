import logging

from celery.signals import setup_logging

@setup_logging.connect
def setup_celery_logging(**kwargs):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s: %(levelname)s] %(message)s"
    )