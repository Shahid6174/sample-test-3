import os
import yaml

from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Defaults
# --------------------

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# --------------------
# YAML
# --------------------

config = defaults.copy()

if os.path.exists("config.development.yaml"):
    with open("config.development.yaml") as f:
        yaml_cfg = yaml.safe_load(f)

    if yaml_cfg:
        config.update(yaml_cfg)

# --------------------
# .env
# --------------------

env_cfg = dotenv_values(".env")

mapping = {
    "APP_PORT": "port",
    "APP_WORKERS": "workers",
    "APP_DEBUG": "debug",
    "APP_LOG_LEVEL": "log_level",
    "APP_API_KEY": "api_key",
    "NUM_WORKERS": "workers",
}

for k, v in env_cfg.items():
    if k in mapping:
        config[mapping[k]] = v

# --------------------
# OS Environment
# --------------------

for k, v in os.environ.items():
    if k.startswith("APP_"):
        config[k[4:].lower()] = v

# --------------------
# Helpers
# --------------------

def to_bool(v):
    return str(v).lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def convert(cfg):

    cfg["port"] = int(cfg["port"])
    cfg["workers"] = int(cfg["workers"])
    cfg["debug"] = to_bool(cfg["debug"])
    cfg["log_level"] = str(cfg["log_level"])

    if "api_key" in cfg:
        cfg["api_key"] = str(cfg["api_key"])

    return cfg


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):

    result = config.copy()

    # CLI overrides
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)
        result[key] = value

    result = convert(result)

    # Mask secret
    result["api_key"] = "****"

    return result