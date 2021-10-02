TRANSLATIONS = {"hi": "Hola"}


def gettext(key):
    return TRANSLATIONS.get(key, key)


def pretty_date(date):
    if date is None:
        return "N/A"
    return date.strftime("%d/%m/%Y")
