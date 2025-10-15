# Dockerfile pour tester wcrp-cmip6_plugin de façon isolée
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt

# paquets système nécessaires pour construire/faire fonctionner netCDF4, PROJ, GEOS, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    git \
    ca-certificates \
    wget \
    curl \
    pkg-config \
    libhdf5-dev \
    libnetcdf-dev \
    libproj-dev proj-bin \
    libgeos-dev \
    libxml2-dev libxslt1-dev \
    libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# pip + outils
RUN python -m pip install --upgrade pip setuptools wheel

# Installer compliance-checker (dernier stable) et outils utiles
RUN pip install compliance-checker netCDF4 xarray pandas cftime toml

# (optionnel) si ton plugin dépend d'esgvoc et que c'est dispo sur PyPI
RUN pip install esgvoc

# Copier ton plugin dans l'image (optionnel; tu peux aussi le monter en volume)
# Si tu veux builder en copiant le projet dans l'image, assure-toi que ton contexte de build contient le dossier.
COPY  . /app/



# Entrypoint : démarrer un shell par défaut
ENTRYPOINT ["/bin/bash"]

