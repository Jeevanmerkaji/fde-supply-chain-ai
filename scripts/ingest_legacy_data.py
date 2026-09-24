from pathlib import Path
import pandas as pd
import urllib
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


script_dir =  Path(__file__).resolve().parent
project_root  = script_dir
