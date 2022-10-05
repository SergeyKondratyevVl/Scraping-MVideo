from numpy import arange
import requests
import json
from config import cookies, headers
import os


def get_data(category_id=1):

    # category_id = 205

    params = {
        'categoryId': f'{category_id}',
        'offset': '0',
        'limit': '24',
        'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiLTEyIiwiZGEiXQ==',
        'doTranslit': 'true',
    }
    
    s = requests.Session()
    response = s.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies, headers=headers).json()

    total_items = response.get('body').get('total')
    
    if total_items is None:
        return '[!] No items :('

    page_counts = total_items // 24 + 1

    if not os.path.exists(f'data/category_{category_id}'):
        os.mkdir(f'data/category_{category_id}')

    print(f'[INFO] Total positions: {total_items} | Total pages: {page_counts} | Category: {category_id}\n')

    products_ids = {}
    products_description = {}
    products_prices = {}

    for i in range(page_counts):
        try:
            offset = f'{i * 24}'

            params = {
                'categoryId': f'{category_id}',
                'offset': offset,
                'limit': '24',
                'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiLTEyIiwiZGEiXQ==',
                'doTranslit': 'true',
            }

            response_listing = s.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies, headers=headers).json()

            products_ids_list = response_listing.get('body').get('products')
            products_ids[i] = products_ids_list

            json_data = {
                'productIds': products_ids_list,
                'mediaTypes': [
                    'images',
                ],
                'category': True,
                'status': True,
                'brand': True,
                'propertyTypes': [
                    'KEY',
                ],
                'propertiesConfig': {
                    'propertiesPortionSize': 5,
                },
                'multioffer': False,
            }

            response_list = s.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers, json=json_data).json()

            products_description[i] = response_list.get('body').get('products')

            name_translit = products_description[i][0].get('nameTranslit')

            products_ids_str = ','.join(products_ids_list)

            params = {
                'productIds': products_ids_str,
                'addBonusRubles': 'true',
                'isPromoApplied': 'true',
            }

            response_prices = s.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies, headers=headers).json()

            material_prices = response_prices.get('body').get('materialPrices')

            for item in material_prices:
                item_id = item.get('price').get('productId')
                item_base_price = item.get('price').get('basePrice')
                item_sale_price = item.get('price').get('salePrice')
                item_bonus = item.get('bonusRubles').get('total')
                item_discount = item_base_price - item_sale_price

                products_prices[item_id] = {
                    'itemBasePrice': item_base_price,
                    'itemSalePrice': item_sale_price,
                    'itemBonus': item_bonus,
                    'itemDiscount': item_discount,
                    'itemLink': f'https://www.mvideo.ru/products/{name_translit}-{item_id}/'
                }

            print(f'[+] Finished {i+1} of the {page_counts} pages')
        
        except Exception as ex:
            print(ex)

        with open(f'data/category_{category_id}/1_products_ids.json', 'w', encoding='utf-8') as file:
            json.dump(products_ids, file, indent=4, ensure_ascii=False)
        with open(f'data/category_{category_id}/2_products_description.json', 'w', encoding='utf-8') as file:
            json.dump(products_description, file, indent=4, ensure_ascii=False)
        with open(f'data/category_{category_id}/3_products_prices.json', 'w', encoding='utf-8') as file:
            json.dump(products_prices, file, indent=4, ensure_ascii=False)
        

    
def main():
    for category_id in [34,]:
        get_data(category_id=category_id)


if __name__ == '__main__':
    main()