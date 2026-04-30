import unicodedata

def generate_slug(name: str):
    slug = unicodedata.normalize('NFKD', name)
    slug = slug.encode('ascii', 'ignore').decode('ascii')
    slug = slug.lower().replace(" ", "-")
    return slug