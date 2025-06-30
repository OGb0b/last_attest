from g4f.client import Client
import requests

def generate_description(product_name: str, business_description: str, target_audience: str):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Составь краткое, продающее описание товара на русском языке для карточки интернет-магазина. Учитывай следующие данные о бизнесе:\n\nОписание бизнеса: {business_description}\nЦелевая аудитория: {target_audience}\n\nБез приветствий, лишних пояснений и вводных фраз — только готовый текст описания, как для вывода на сайте. Используй простой, понятный стиль. Товар: {product_name}"}
        ],
        web_search=False
    )
    return response.choices[0].message.content

def generate_ad_text(product_name: str, business_description: str, target_audience: str):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Составь краткий, продающий рекламный текст для товара на русском языке. Учитывай следующие данные о бизнесе:\n\nОписание бизнеса: {business_description}\nЦелевая аудитория: {target_audience}\n\nБез приветствий, лишних пояснений и вводных фраз — только готовый текст для рекламы. Товар: {product_name}"}
        ]
    )
    return response.choices[0].message.content



def generate_product_card(product_name: str, business_description: str, target_audience: str):
    client = Client()
    

    prompt_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"сгенерируй промпт на английском языке для создания карточки товара:{product_name}, описание бизнеса:{business_description}, целевая аудитория:{target_audience}"}
        ],
        web_search=False
    )
    prompt = prompt_response.choices[0].message.content
    

    image_response = client.images.generate(
        model="flux",
        prompt=prompt,
        response_format="url"
    )
    return image_response.data[0].url

def generate_ad_text(product_name: str, business_description: str, target_audience: str):
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content":
             f"""Придумай яркий, эмоциональный и запоминающийся рекламный текст на русском языке для продвижения товара.

Текст должен быть в разговорном, живом и цепляющем стиле — как для баннера, Instagram-рекламы или сайта. Избегай банальностей и канцелярщины. Используй стиль, соответствующий бизнесу.

Напиши только рекламный текст — без пояснений и приветствий.

Товар: {product_name}
Целевая аудитория: {target_audience}
О бизнесе: {business_description}"""}
        ],
        web_search=False
    )
    return response.choices[0].message.content