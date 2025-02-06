import typer
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import List
import shutil
import os



DEFAULT_IP = "http://localhost:"
DEFAULT_PORT = "8080"
GET_ALL_SOLDERPASTES = "/dev/data-management/entries/solder-paste"
POST_NEW_SOLDERPASTE = "/dev/data-management/entries/solder-paste"
GET_ONE_SOLDERPASTE = "/dev/data-management/entries/"
DELETE_ONE_SOLDERPASTE = "/dev/data-management/entries/"

app = typer.Typer()

@app.command()
def get_single_solderpaste(uuid: str, ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Displays and returns details of a single solder paste."""
    url = f"{ip}{port}{GET_ONE_SOLDERPASTE}{uuid}"
    print(f"Retrieving details for solder paste UUID: {uuid} from {url}")

    try:
        response = requests.get(url)
        data = response.json() 

        print("Status Code:", response.status_code)
        print("Response JSON:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        return data 

    except requests.RequestException as e:
        print(f"Error fetching solder paste details: {e}")
        return None  
    
@app.command()
def list_all_solder_pastes(ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Displays all installed solder pastes and returns the data."""
    url = f"{ip}{port}{GET_ALL_SOLDERPASTES}"
    print(f"Retrieving list of solder pastes from {url}")

    try:
        response = requests.get(url)
        data = response.json()  

        print("Status Code:", response.status_code)
        print("Response JSON:")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        return data  
    
    except requests.RequestException as e:
        print(f"Error fetching solder pastes: {e}")
        return None  
     
@app.command()
def list_all_solder_pastes_as_uuids(ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Displays all installed solder pastes as a list of UUIDs and returns them."""
    
    url = f"{ip}{port}{GET_ALL_SOLDERPASTES}"
    print(f"Retrieving list of solder pastes from {url}")

    try:
        response = requests.get(url)
        response_json = response.json()

    except requests.exceptions.JSONDecodeError:
        print("Error: The response does not contain valid JSON.")
        return None
    except requests.RequestException as e:
        print(f"Error fetching solder pastes: {e}")
        return None

    if isinstance(response_json, list):
        uuid_list = [obj.get("uuid") for obj in response_json if "uuid" in obj]
    else:
        print("Error: Expected a JSON list but received:", type(response_json))
        return None

    print("Status Code:", response.status_code)
    print("UUIDs as list:", uuid_list)

    return uuid_list

@app.command()
def add_solder_paste(json_file: Path, ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Parses a JSON file, constructs the required object, and sends it to the API."""
    typer.echo("Reading solder paste data from file...")

    try:
        with json_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        typer.echo("Error: File not found.")
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        typer.echo("Error: Invalid JSON format.")
        raise typer.Exit(code=1)

    if "meta" not in data:
        typer.echo("Error: JSON file is missing 'meta' field.")
        raise typer.Exit(code=1)

    meta = data["meta"]

    solder_paste_payload = {
        "meta": {
            "created": meta.get("created", datetime.now().isoformat()),
            "updated": meta.get("updated", datetime.now().isoformat()),
            "author": meta.get("author", None),
            "name": meta["name"],
            "manufacturer": meta["manufacturer"],
            "hersteller": meta.get("hersteller", ""),
            "mpn": meta["mpn"],
            "price": meta.get("price", None), 
            "temp_rules": meta.get("temp_rules", []),
            "thickness": meta.get("thickness", 0),
            "elements": meta.get("elements"),
            "package": meta.get("package"),
            "type": meta["type"],
            "category": meta["category"]
        }
    }

    url = f"{ip}{port}{POST_NEW_SOLDERPASTE}"
    response = requests.post(url, json=solder_paste_payload)

    typer.echo(f"Payload: {json.dumps(solder_paste_payload, indent=4, ensure_ascii=False)}")
    typer.echo(f"Response JSON: {json.dumps(response.json(), indent=4, ensure_ascii=False)}")
    typer.echo(f"Response Status Code: {response.status_code}")
    typer.echo(f"Upload Solder-paste successfull");
    
@app.command()
def add_multiple_solder_pastes(json_files: List[Path], ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Processes multiple JSON files and sends them to the API one by one."""
    for json_file in json_files:
        typer.echo(f"Processing file: {json_file}")
        add_solder_paste(json_file, ip, port)

@app.command()
def delete_solder_paste(uuid: str, ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Deletes a solder paste by UUID."""
    typer.echo(f"Deleting solder paste with UUID {uuid} from {url}")
    
    url = f"{ip}{port}{DELETE_ONE_SOLDERPASTE}{uuid}"
    response = requests.delete(url)
    
    if response.status_code == 200:
        typer.echo(f"Response: File with UUID: {uuid} was successfully deleted")
    else:
        typer.echo("Response: Deletion failed")

@app.command()
def delete_multiple_solder_pastes(uuids: List[str], ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Deletes multiple solder pastes by their UUIDs."""
    for uuid in uuids:
        typer.echo(f"Processing deletion for UUID: {uuid}")
        delete_solder_paste(uuid, ip, port)
    


@app.command()
def import_file(file_path: Path):
    """Imports a file and copies it to the user's Roaming directory under 'Horus Desktop App/resources/ptp_data'. IMPORTANT filename must be the uuid of the paste!!!"""
    
    user_appdata = Path(os.getenv("APPDATA"))  
    target_directory = user_appdata / "Horus Desktop App" / "resources" / "ptp_data"
    target_directory.mkdir(parents=True, exist_ok=True)
    target_file_path = target_directory / file_path.name

    try:
        shutil.copy(file_path, target_file_path)
        typer.echo(f"Import successful: {file_path} -> {target_file_path}")
    except Exception as e:
        typer.echo(f"Error importing file: {e}")
        raise typer.Exit(code=1)

    
@app.command()
def export_solder_paste(uuid: str, output: Path = Path("."), ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Exports a solder paste as a JSON file to the specified directory."""

    typer.echo(f"Fetching solder paste details for UUID: {uuid}...")
    data = get_single_solderpaste(uuid, ip, port)

    if not data or "meta" not in data:
        typer.echo(f"Error: No valid data retrieved for UUID {uuid}.")
        raise typer.Exit(code=1)

    meta = data["meta"]  

    # Ensure the output directory exists
    output.mkdir(parents=True, exist_ok=True)

    file_path = output / f"{uuid}"

    mapped_data = {
        "meta": {
            "uuid": meta.get("uuid"),
            "name": meta.get("name"),
            "manufacturer": meta.get("manufacturer"),
            "hersteller": meta.get("hersteller", ""),
            "mpn": meta.get("mpn"),
            "price": meta.get("price"),
            "temp_rules": meta.get("temp_rules", []),
            "thickness": meta.get("thickness", 0),
            "type": meta.get("type"),
            "category": meta.get("category"),
            "created": meta.get("created"),
            "updated": meta.get("updated"),
        }
    }

    try:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(mapped_data, file, indent=4, ensure_ascii=False)
        typer.echo(f"Export successful: {file_path}")
    except IOError as e:
        typer.echo(f"Error writing file: {e}")
        raise typer.Exit(code=1)

@app.command()
def export_multiple_solder_pastes(uuids: List[str], output: Path = Path("."), ip: str = DEFAULT_IP, port: str = DEFAULT_PORT):
    """Exports multiple solder pastes as JSON files to the specified directory."""
    
    # Ensure the output directory exists
    output.mkdir(parents=True, exist_ok=True)

    for uuid in uuids:
        typer.echo(f"Exporting solder paste for UUID: {uuid}...")
        export_solder_paste(uuid, output, ip, port)

if __name__ == "__main__":
    app() 
