FROM python:3.10-slim

WORKDIR /app

# Install clickhouse-client
RUN apt-get update && \
    apt-get install -y wget apt-transport-https ca-certificates dirmngr && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754 && \
    echo "deb https://packages.clickhouse.com/deb stable main" | tee /etc/apt/sources.list.d/clickhouse.list && \
    apt-get update && \
    apt-get install -y clickhouse-client && \
    rm -rf /var/lib/apt/lists/*

# Copy all necessary application directories from the build context (project root)
COPY etl/ /app/etl/
COPY data/ /app/data/
COPY database/ /app/database/
COPY database/views/ /app/views/

# Install Python dependencies from the requirements file copied in the previous step
RUN pip install -r /app/etl/requirements.txt

# Create initialization script that runs all .sql files and loads CSV
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Waiting for Clickhouse to be ready..."\n\
until clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --query "SELECT 1";\n\
do\n\
    echo "Clickhouse is unavailable - sleeping 5s"\n\
    sleep 5\n\
done\n\
\n\
echo "Creating staging schema..."\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --multiquery < /app/database/staging_schema.sql\n\
\n\
echo "Creating star schema..."\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --multiquery < /app/database/star_schema.sql\n\
\n\
echo "Loading initial production data..."\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --multiline < /app/database/production_logs.sql\n\
\n\
echo "Loading equipment sensor data from CSV..."\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --query="INSERT INTO staging.equipment_sensors FORMAT CSVWithNames" < /app/data/equipment_sensors.csv\n\
\n\
echo "Creating analytical views..."\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --multiquery < /app/views/analytical_views.sql\n\
\n\
echo "Verifying data load..."\n\
echo "Checking mines table:"\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --query "SELECT count(*) FROM staging.mines;"\n\
echo "Checking production_logs table:"\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --query "SELECT count(*) FROM staging.production_logs;"\n\
echo "Checking equipment_sensors table:"\n\
clickhouse-client --host clickhouse --user $CLICKHOUSE_USER --password $CLICKHOUSE_PASSWORD --query "SELECT count(*) FROM staging.equipment_sensors;"\n\
\n\
echo "Initialization complete."\n' > /app/init.sh && chmod +x /app/init.sh

# Create the log file to be able to run tail
RUN touch /var/log/etl.log

# Default: do nothing (ETL should be run manually)
CMD ["tail", "-f", "/dev/null"] 