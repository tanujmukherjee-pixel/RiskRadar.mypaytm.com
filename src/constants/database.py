import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://admin:Freshwater%40123@172.21.5.177:5432/agency")
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "https://maquette-es.internal.ap-south-1.production.osmose.risk.pai.mypaytm.com:443")