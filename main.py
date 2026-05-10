# Importiamo Enum per creare elenchi di valori predefiniti
from enum import Enum

# Importiamo la classe FastAPI, cuore del framework
from fastapi import FastAPI

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