FROM prom/prometheus:latest

# Copy the configuration files into the image
COPY monitoring/prometheus.yml /etc/prometheus/prometheus.yml
COPY monitoring/alerts.yml /etc/prometheus/alerts.yml

# Set user to root temporarily to ensure correct permissions
USER root
RUN chmod 644 /etc/prometheus/prometheus.yml /etc/prometheus/alerts.yml
# Switch back to nobody user (prometheus default)
USER nobody
