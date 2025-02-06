import typer

app = typer.Typer() 

@app.command()
def list_solder_pastes(ip: str, port: int):
    """Displays all installed solder pastes."""
    typer.echo(f"Retrieving list of solder pastes from {ip}:{port}")

@app.command()
def add_solder_paste(ip: str, port: int, json_file: str):
    """Adds a solder paste from a JSON file."""
    typer.echo(f"Adding solder paste from {json_file} to {ip}:{port}")

@app.command()
def delete_solder_paste(ip: str, port: int, uuid: str):
    """Deletes a solder paste by UUID."""
    typer.echo(f"Deleting solder paste with UUID {uuid} from {ip}:{port}")

@app.command()
def export_solder_paste(ip: str, port: int, uuid: str, output: str):
    """Exports a solder paste as a ZIP file."""
    typer.echo(f"Exporting solder paste with UUID {uuid} to {output} from {ip}:{port}")

if __name__ == "__main__":
    app() 
