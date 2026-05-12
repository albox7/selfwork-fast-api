# Importiamo Enum per creare elenchi di valori predefiniti
from enum import Enum

# Importiamo BaseModel di Pydantic per definire modelli di dati con validazione automatica
from pydantic import BaseModel

# Importiamo anche Query per aggiungere validazioni ai query parameters
from fastapi import FastAPI, Query

# Annotated permette di "annotare" un tipo con metadati aggiuntivi (es. validazioni)
from typing import Annotated

# Importiamo la classe FastAPI, cuore del framework
from fastapi import FastAPI

# Importiamo anche Path per aggiungere validazioni ai path parameters
from fastapi import FastAPI, Query, Path

# Importiamo BaseModel per i modelli di dati, e Field per aggiungere vincoli ai campi
from pydantic import BaseModel, Field




# Creiamo l'istanza dell'applicazione
app = FastAPI()


# --- ROTTA HOMEPAGE ---
# Risponde alle richieste GET sulla radice "/"
@app.get("/")
async def root():
    return {"message": "Ciao Mondo"}



# --- PATH PARAMETER TIPIZZATO ---
# item_id è dichiarato come int: FastAPI lo converte e valida automaticamente.
# Se l'utente passa qualcosa che non è un numero, restituisce un errore 422.
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}



# --- ORDINE DELLE ROTTE ---
# La rotta fissa "/users/me" DEVE essere dichiarata prima di quella dinamica
# "/users/{user_id}", altrimenti "me" verrebbe interpretato come user_id.
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "utente corrente"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}



# --- PATH PARAMETER CON ENUM ---
# Definiamo un insieme chiuso di valori accettati.
# Ereditando da str, i valori sono usabili anche come stringhe.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"



# Solo "alexnet", "resnet" o "lenet" sono accettati: qualsiasi altro valore
# produce un errore di validazione.
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
   
    # Confronto tramite l'enum stesso
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    
	# Confronto tramite il valore stringa
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    
	# Default: resnet
    return {"model_name": model_name, "message": "Have some residuals"}



# --- PATH PARAMETER CHE CONTIENE UN PERCORSO ---
# La sintassi {file_path:path} consente di passare URL con slash interni,
# es. /files/home/utente/file.txt → file_path = "home/utente/file.txt"
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}



# --- QUERY PARAMETERS ---
# I parametri che NON fanno parte del path sono interpretati come query parameters.
# Vengono passati nell'URL dopo "?" e separati da "&", es: /items_q/?skip=0&limit=10
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items_q/")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]



# --- QUERY PARAMETER OPZIONALE ---
# "q" ha default None: se non specificato nell'URL, viene ignorato.
# item_id è path parameter, q è query parameter (FastAPI lo capisce dal nome).
@app.get("/items_opt/{item_id}")
async def read_item_opt(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}



# --- CONVERSIONE AUTOMATICA DI TIPO ---
# "short" è bool: FastAPI converte stringhe come "1", "true", "yes", "on" in True
# e "0", "false", "no", "off" in False.
@app.get("/items_bool/{item_id}")
async def read_item_bool(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Questo è un elemento con una descrizione lunga."})
    return item



# --- PIÙ PATH + QUERY PARAMETERS ---
# user_id e item_id sono path parameters; q e short sono query parameters.
# FastAPI distingue automaticamente in base al nome dichiarato nel path.
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "Questo è un elemento con una descrizione lunga."})
    return item



# --- QUERY PARAMETER OBBLIGATORIO ---
# "needy" non ha valore di default → è obbligatorio.
# Se omesso nell'URL, FastAPI restituisce un errore 422.
@app.get("/items_needy/{item_id}")
async def read_item_needy(item_id: str, needy: str):
    return {"item_id": item_id, "needy": needy}



# --- MIX DI PARAMETRI ---
# needy: obbligatorio (nessun default)
# skip: ha un valore di default (0) → opzionale
# limit: opzionale (None se non specificato)
@app.get("/items_mix/{item_id}")
async def read_item_mix(item_id: str, needy: str, skip: int = 0, limit: int | None = None):
    return {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}



# --- REQUEST BODY CON PYDANTIC ---
# BaseModel di Pydantic permette di definire la struttura dei dati attesi.
# FastAPI valida automaticamente il JSON inviato dal client.
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# POST: il client invia un JSON nel body, FastAPI lo converte in oggetto Item.
@app.post("/items/")
async def create_item(item: Item):
    return item



# --- ACCESSO AGLI ATTRIBUTI DEL MODELLO ---
# Dentro la funzione possiamo leggere ogni campo come attributo dell'oggetto.
# model_dump() converte l'oggetto Pydantic in un dizionario Python.
@app.post("/items_calc/")
async def create_item_calc(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict



# --- REQUEST BODY + PATH PARAMETER ---
# Combiniamo body (Item) e path parameter (item_id).
# PUT è il metodo HTTP tipico per aggiornare una risorsa esistente.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}



# --- REQUEST BODY + PATH + QUERY PARAMETER ---
# Combiniamo tutto: path (item_id), body (item) e query (q).
@app.put("/items_full/{item_id}")
async def update_item_full(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result



# --- VALIDAZIONE QUERY PARAMETER ---
# Query() permette di aggiungere vincoli al parametro:
# qui imponiamo che q (se fornito) abbia al massimo 50 caratteri.
@app.get("/items_val/")
async def read_items_val(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results



# --- VALIDAZIONI MULTIPLE ---
# min_length: lunghezza minima
# max_length: lunghezza massima
# pattern: regex che il valore deve rispettare (qui deve essere esattamente "fixedquery")
@app.get("/items_val2/")
async def read_items_val2(
    q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results



# --- VALIDAZIONE PATH PARAMETER ---
# Path() aggiunge metadati e validazioni numeriche ai path parameter.
# title: descrizione mostrata nella documentazione.
# ge=1: greater than or equal → item_id deve essere >= 1.
# Si possono usare anche: gt (greater than), le (less or equal), lt (less than).
@app.get("/items_val3/{item_id}")
async def read_items_val3(item_id: Annotated[int, Path(title="ID dell'elemento", ge=1)]):
    return {"item_id": item_id}



# --- MODELLO PYDANTIC PER I QUERY PARAMETERS ---
# Quando i query parameters sono molti, conviene raggrupparli in un modello.
# model_config = {"extra": "forbid"} → se il client invia parametri extra non
# previsti, FastAPI restituisce un errore (utile per evitare typo).
class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}
    limit: int = Field(100, gt=0, le=100)   # default 100, deve essere 1-100
    offset: int = Field(0, ge=0)            # default 0, deve essere >= 0
    order_by: str = "created_at"
    tags: list[str] = []

# Annotated[FilterParams, Query()] dice a FastAPI di leggere i campi dal query string.
@app.get("/items_filter/")
async def read_items_filter(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


