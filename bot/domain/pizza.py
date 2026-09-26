PIZZA_TYPE = {
    "margherita": "Маргарита",
    "pepperoni": "Пеппероні",
    "four_cheeses": "Чотири сира",
    "hawaiian": "Гавайська",
    "bbq_chicken": "Куриця барбекю",
    "all_meet": "М'ясна",
    "vegetarian": "Вегетаріанська",
}

PIZZA_SIZE = {
    "size_small": "Маленька (25 см.)",
    "size_medium": "Середня (30 см.)",
    "size_large": "Велика (35 см.)",
    "size_super": "Дуже велика (40 см.)",
}

DRINKS = {
    "coca_cola": "Кока-кола",
    "pepsi": "Пепсі",
    "orange_jus": "Апельсиновий сік",
    "apple_jus": "Яблучний сік",
    "no_drinks": "Без напою",
}

# order_data - {"pizza_type": PIZZA_TYPE_key, "pizza_size": PIZZA_SIZE_key, "drink": DRINKS_key}


def build_keyboard(keyboard: dict) -> list:
    result = []
    Index = 0
    for key, value in keyboard.items():
        row, column = divmod(Index, 2)
        if column == 0:
            result.append([])
        result[row].append({"text": value, "callback_data": key})
        Index += 1  # noqa: SIM113

    return result


def build_pizza_type_keyboard() -> list:
    return build_keyboard(PIZZA_TYPE)


def build_pizza_size_keyboard() -> list:
    return build_keyboard(PIZZA_SIZE)


def build_drinks_keyboard() -> list:
    return build_keyboard(DRINKS)


def is_exits_pizza_type(key: str) -> bool:
    return key in PIZZA_TYPE


def is_exists_pizza_size(key: str) -> bool:
    return key in PIZZA_SIZE


def is_exists_drinks(key: str) -> bool:
    return key in DRINKS


def get_pizza_type(key: str) -> str:
    return PIZZA_TYPE.get(key)


def get_pizza_size(key: str) -> str:
    return PIZZA_SIZE.get(key)


def get_drinks(key: str) -> str:
    return DRINKS.get(key)


if __name__ == "__main__":
    print("keyboard for type")
    print(build_pizza_type_keyboard())
    print("keyboard for size")
    print(build_pizza_size_keyboard())
