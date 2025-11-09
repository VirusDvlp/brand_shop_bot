

def get_good_card_text(name: str, descr: str, usage: str, volume: str, price: str):
    return f"""
<b>Название</b>: {name}

<b>Описание</b>

{descr}

<b>Показания к применению</b>:
{usage}

<b>Объем</b>: {volume}

<b>Цена</b>: {price}
"""[:1023]
