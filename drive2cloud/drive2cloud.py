import logging
from time import sleep

import click
from datetime import timedelta

from app import App

logging.basicConfig(format='%(asctime)s: [%(levelname)s] - %(message)s',
                    handlers=[logging.StreamHandler(), logging.FileHandler('log')],
                    level='INFO')


@click.command()
@click.option('--reindex', default=False, type=bool, help='Rebuild uploaded files index on start.')
@click.option('--interval-hours', type=int, help='Schedule interval in hours.')
def run(reindex, interval_hours):
    interval = timedelta(hours=interval_hours) if interval_hours else None

    app = App(reindex)
    app.run()

    if interval is None:
        logging.info('completed')
        return

    while True:
        logging.info(f'app will be rescheduled in {interval}')
        sleep(interval.seconds)
        app.run()


if __name__ == '__main__':
    run()
