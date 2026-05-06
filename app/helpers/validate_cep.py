import requests

def is_valid_cep(cep: str):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep}/json")
        if response.status_code == 200:
            data = response.json()
            if "erro" in data:
                return False
            return data
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False