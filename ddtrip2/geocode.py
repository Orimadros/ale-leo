from geopy.geocoders import Nominatim
from time import sleep

amigos = [
  {"nome": "Ale", "endereco": "Morumbi", "pais": "Brasil"},
  {"nome": "Fracassi", "endereco": "Morumbi", "pais": "Brasil"},
  {"nome": "Bá", "endereco": "Vila Olímpia", "pais": "Brasil"},
  {"nome": "Bi Finotti", "endereco": "Ipiranga", "pais": "Brasil"},
  {"nome": "Bibs Oliveira", "endereco": "Vila Olímpia", "pais": "Brasil"},
  {"nome": "Bru", "endereco": "Itaim Bibi", "pais": "Brasil"},
  {"nome": "Dogo", "endereco": "Vila Nova Conceição", "pais": "Brasil"},
  {"nome": "Edu", "endereco": "Vila Olímpia", "pais": "Brasil"},
  {"nome": "Faia", "endereco": "Vila Nova Conceição", "pais": "Brasil"},
  {"nome": "Gabi Di Fiori", "endereco": "Vila Olímpia", "pais": "Brasil"},
  {"nome": "Leo Veras", "endereco": "Paraíso", "pais": "Brasil"},
  {"nome": "Leo Gomes", "endereco": "Hell's Kitchen", "pais": "EUA"},
  {"nome": "Math Belarmino", "endereco": "Guarulhos", "pais": "Brasil"},
  {"nome": "Pedrão", "endereco": "Panamby", "pais": "Brasil"},
  {"nome": "Rafa", "endereco": "Morumbi", "pais": "Brasil"},
  {"nome": "Valen", "endereco": "Vila Nova Conceição", "pais": "Brasil"},
  {"nome": "Rennan", "endereco": "São Caetano", "pais": "Brasil"},
  {"nome": "Ju", "endereco": "Morumbi", "pais": "Brasil"}
]

# identifique-se com um user_agent bonitinho (recomendado pelo Nominatim)
geolocator = Nominatim(user_agent="viagem-justa-amigos/1.0 (email@exemplo.com)")

def montar_query(amigo):
    # quase todo mundo está na Grande São Paulo, então ajuda a refinar
    if amigo["pais"] == "Brasil":
        # se não tiver cidade, você pode chutar "São Paulo" pra bairros/bairros-zona sul
        # e ajustar depois se precisar
        return f"{amigo['endereco']}, São Paulo, Brasil"
    else:
        return f"{amigo['endereco']}, {amigo['pais']}"

resultado = {}

for amigo in amigos:
    query = montar_query(amigo)
    print(f"Buscando '{amigo['nome']}' -> {query}")
    try:
        location = geolocator.geocode(query, addressdetails=False, timeout=10)
    except Exception as e:
        print(f"  Erro ao geocodificar {amigo['nome']}: {e}")
        continue

    if location is None:
        print(f"  Não encontrado 😢")
        continue

    lat = location.latitude
    lon = location.longitude

    resultado[amigo["nome"]] = {"lat": lat, "lon": lon}
    print(f"  OK: lat={lat:.6f}, lon={lon:.6f}")

    # Nominatim pede pra não spammar requests – 1seg entre elas é educado
    sleep(1)

import json

# 1. Carrega seu arquivo existente
with open("gestao.json", "r", encoding="utf-8") as f:
    amigos_json = json.load(f)

# 2. Insere lat/lon em cada amigo correspondente
for amigo in amigos_json:
    nome = amigo["nome"]
    if nome in resultado:
        amigo["lat"] = resultado[nome]["lat"]
        amigo["lon"] = resultado[nome]["lon"]
    else:
        print(f"Sem coordenadas para {nome}, pulando...")

# 3. Salva de volta no arquivo (ou em outro se quiser preservar o original)
with open("gestao.json", "w", encoding="utf-8") as f:
    json.dump(amigos_json, f, ensure_ascii=False, indent=2)

print("\nArquivo 'gestao.json' atualizado com lat/lon!")

print("\nDICIONÁRIO FINAL:")
print(resultado)