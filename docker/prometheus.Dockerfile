FROM prom/prometheus:latest

COPY monitoring/prometheus.yaml /etc/prometheus/prometheus.yml
COPY monitoring/alerts.yaml /etc/prometheus/alerts.yml

USER root
RUN chmod 644 /etc/prometheus/prometheus.yml /etc/prometheus/alerts.yml
USER nobody
