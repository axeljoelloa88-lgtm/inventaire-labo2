FROM postgres:15

# Copier le script SQL dans le dossier d'initialisation
COPY init/01_schema.sql /docker-entrypoint-initdb.d/

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}
