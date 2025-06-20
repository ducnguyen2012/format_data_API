from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
#print(f"This is my base_dir: {base_dir}")
dotenv_path = base_dir /'.env'
load_dotenv(dotenv_path)