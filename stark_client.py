import os
from dotenv import load_dotenv
import starkbank

load_dotenv()

def get_required_env(envName: str) -> str:
    e = os.getenv(envName)
    if not e:
        raise ValueError(f"A variável de ambiente {envName} não foi configurada ou está vazia.")
    return e

private_key_path = get_required_env("privateKeyPath")
try:
    with open(private_key_path, 'r', encoding='utf-8') as f:
        private_key_content = f.read()
except FileNotFoundError as e:
    raise FileNotFoundError(f"Arquivo PEM não encontrado no caminho: {private_key_path}") from e

project = starkbank.Project(
    environment="sandbox",
    id=get_required_env("projectID"),
    private_key=private_key_content
)