# FastAPI Tutorial with Basic PyQuery Project
import os
import json
import random
import shutil
from fastapi import FastAPI, HTTPException, UploadFile
from typing import  Union
from pyquery import PyQuery
from pydantic import BaseModel
from uuid import uuid4 # Universally Unique Identifier

class Item(BaseModel):
    name: str
    description: Union[str, None] = None # Optional value (See in FastAPI/docs)
    price: float
    tax: Union[float, None] = None # Optional value (See in FastAPI/docs)

# Pokedex Link
pokemons_link = 'https://pokemondb.net/pokedex/all'


# Get all information from link (html)
doc = PyQuery(url=pokemons_link)
# Get information under <tr>
pokemons_ = doc.find('tr').children()
# Find out all text value in class 'infocard-cell-data' and split as a list
pokemons_index = pokemons_.find('.infocard-cell-data').text().split(' ')
# Find out all text value in class 'ent-name' and split as a list
pokemons_name = pokemons_.find('.ent-name').text().split(' ')
# Create a dictionary with keys and values
my_pokedex = dict(zip(pokemons_index, pokemons_name))

app = FastAPI()

# Local data initialize
my_items = []
my_file = 'item.json'
my_file_names = []
# Load local json file if exist
if os.path.exists(my_file):
    with open(my_file, "r") as f:
        my_items = json.load(f)

'''
Wrong Example (API Definition Order)
You should define the special path on top !
See <----
'''
# @app.get('/books/{book_id}') <----
# def get_book(book_id: string):
#     print(f'Return book to Client: {book_id}')
#     return book_id
# @app.get('/books/only_for_me') <----
# def get_book_only_for_me(book_id: string):
#     return 'the book that I can read only'

# GET Method Exercise (Basic)
@app.get('/')
async def root():
    return {"message": "FastAPI in Python"}

# GET Method Exercise
@app.get('/random-pokemon')
def random_pokemon():
    return random.choice(list(my_pokedex.items()))

# GET Method Exercise (Interact with local database)
@app.get('/get-pokemon')
def get_pokemon(poke_id: int = 1):
    if poke_id > len(my_pokedex):
        raise HTTPException(404, f"Pokemon ID {poke_id} not in your pokedex")
    else:
        # Turn integer value to string and leading zero as len == 3
        pokemon_id = str(poke_id).zfill(3)
        # Find out if pokemon_id is in database
        if pokemon_id in my_pokedex:
            return {f"Pokemon ID = {pokemon_id}":f"Pokemon Name = {my_pokedex[pokemon_id]}"}
        else:
            raise HTTPException(404, f"Pokemon ID {pokemon_id} not in your pokedex")

# GET Method Exercise
@app.get('/show-pokemons')
async def show_pokemons():
    return {'This is my pokedex' : my_pokedex}

# POST Method Exercise
@app.post('/add-item')
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax":price_with_tax})
    # Generate an UUID with HEX code
    item_id = uuid4().hex
    item_dict.update({"id":item_id})
    my_items.append(item_dict)
    # Save a new item into local database (JSON file)
    with open(my_file, "w") as f:
        json.dump(my_items, f, indent=4)
    return item_dict

# GET/POST Method Result
@app.get('/show-items', response_model=Item, response_model_exclude_unset=True)
async def show_item():
    return {'Items':my_items}

'''
Inorder to recieve upload file
You need to install a new package
>   pip install python-multipart
Because FastAPI didn't have build-in file.save function,
    you need to import another module to help you save file.
>   import shutil
'''
# POST Method Exercise (Upload File & Save to local)
@app.post('/upload')
def Upload_file(file: Union[UploadFile, None] = None):
    if not file: return {"message" : "No file upload"}
    try:
        file_location = './' + file.filename
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
            file.close()
        my_file_names.append(file.filename)
        return {"Result" : "OK"}
    except:
        return {"File Save Error":"Error when loading file or saving file"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app= 'fastapi_tutorial:app', reload= True, host= '127.0.0.1', port= '8000')