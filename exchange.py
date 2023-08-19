import platform
import logging
from datetime import datetime, timedelta
from sys import argv

import aiohttp
import asyncio


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    logging.error(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {url}, {str(err)}")


async def get_exchange(number_of_days=None):
    current_date = datetime.now().date().strftime("%d.%m.%Y")
    currencies = ["EUR", "USD"]
    enter = ""
    if not number_of_days:
        try:
            number_of_days = int(argv[1])    # Кількість днів
            if number_of_days > 10:
                return "You can find out the exchange rate no more than for the last 10 days"
        except IndexError:
            result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={current_date}')
            if result:
                enter += f"\nDate: {current_date}\n"
                for currency_code in currencies:
                    exc, = list(filter(lambda el: el["currency"] == currency_code, result.get("exchangeRate")))
                    enter += f"{currency_code}: purchase: {exc['purchaseRateNB']}, sale: {exc['saleRateNB']}\n"
                return enter
            else:
                return "Failed to retrieve data"
        except ValueError:
            additional_currencies = argv[1].split(",")
            for ch in additional_currencies:
                currencies.append(ch.upper())

            result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={current_date}')
            if result:
                enter += f"\nDate: {current_date}\n"
                for currency_code in currencies:
                    exc, = list(filter(lambda el: el["currency"] == currency_code, result.get("exchangeRate")))
                    enter += f"{currency_code}: purchase: {exc['purchaseRateNB']}, sale: {exc['saleRateNB']}\n"
                return enter
            else:
                return "Failed to retrieve data"
    
        try:
            additional_currencies = argv[2].split(",")    # Додаткові валюти
            for ch in additional_currencies:
                currencies.append(ch.upper())
        except IndexError:
            pass
    
    for i in range(number_of_days):
        if i == 0:
            result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={current_date}')
            if result:
                enter += f"\nDate: {current_date}\n"
                for currency_code in currencies:
                    exc, = list(filter(lambda el: el["currency"] == currency_code, result.get("exchangeRate")))
                    enter += f"{currency_code}: purchase: {exc['purchaseRateNB']}, sale: {exc['saleRateNB']}\n"
        else:
            date = (datetime.now() - timedelta(days=i)).date().strftime("%d.%m.%Y")
            result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={date}')
            if result:
                enter += f"\nDate: {date}\n"
                for currency_code in currencies:
                    exc, = list(filter(lambda el: el["currency"] == currency_code, result.get("exchangeRate")))
                    enter += f"{currency_code}: purchase: {exc['purchaseRateNB']}, sale: {exc['saleRateNB']}\n"
    return enter
        

if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    run = asyncio.run(get_exchange())    # Можна передати у консоль кількість днів та додаткові валюти
    print(run)