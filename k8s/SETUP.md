# Kubernetes Setup

## Ingress Controller

Traefik is used as the ingress controller. Install it once per cluster.

```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update

helm install traefik traefik/traefik \
  --namespace traefik \
  --create-namespace \
  --set ports.web.nodePort=30080 \
  --set ports.websecure.nodePort=30443 \
  --set service.type=NodePort \
  --wait --timeout=120s
```

## Deploy

```bash
helm install payzee ./k8s/helm \
  --namespace dev \
  --create-namespace \
  --set secrets.geminiApiKey="<key>" \
  --set secrets.jwtSecretKey="<key>" \
  --set secrets.sentryDsn="<dsn>" \
  --set secrets.sentryEnv="production" \
  --set ingress.host="payzee.example.com"
```

### Upgrade

```bash
helm upgrade payzee ./k8s/helm \
  --namespace dev \
  --set secrets.geminiApiKey="<key>" \
  --set secrets.jwtSecretKey="<key>" \
  --set secrets.sentryDsn="<dsn>" \
  --set secrets.sentryEnv="production" \
  --set ingress.host="payzee.example.com"
```

### Override file (recommended for repeated deploys)

Create `k8s/helm/values-override.yaml` (gitignored):

```yaml
secrets:
  geminiApiKey: "<key>"
  jwtSecretKey: "<key>"
  sentryDsn: "<dsn>"
  sentryEnv: "production"

ingress:
  host: "payzee.example.com"
```

Then run:

```bash
helm upgrade --install payzee ./k8s/helm \
  --namespace dev \
  --create-namespace \
  -f k8s/helm/values-override.yaml
```

## Verify

```bash
# Pod status
kubectl get pods -n dev

# All resources
kubectl get all -n dev

# Ingress
kubectl get ingress -n dev
```

Expected pods: `payzee-api` (x2), `payzee-redis-0`, `payzee-redisinsight`.

## Access

### Via ingress

Add the cluster IP to `/etc/hosts` (or equivalent):

```
<cluster-ip>  payzee.example.com
```

Then access `http://payzee.example.com/health`.

### Via port-forward (local/minikube)

```bash
# API directly
kubectl port-forward svc/payzee-api 8080:8000 -n dev
# http://localhost:8080

# Through Traefik ingress
kubectl port-forward svc/traefik 8080:80 -n traefik
# http://localhost:8080 with Host: payzee.example.com header

# RedisInsight
kubectl port-forward svc/payzee-redisinsight 5540:5540 -n dev
# http://localhost:5540
```

## Local (minikube)

```bash
# Build and load image
docker build -f docker/Dockerfile.dev -t areebahmeddd/payzee:local .
minikube image load areebahmeddd/payzee:local

# Deploy with local image
helm upgrade --install payzee ./k8s/helm \
  --namespace dev \
  --create-namespace \
  -f k8s/helm/values-override.yaml \
  --set api.image.tag=local \
  --set api.image.pullPolicy=Never \
  --set ingress.tls.enabled=false
```

## Debugging

```bash
# Describe a failing pod (shows events, errors, OOMKilled reason, etc.)
kubectl describe pod <pod-name> -n dev

# Stream logs from the API
kubectl logs -f deployment/payzee-api -n dev

# Logs from a specific pod
kubectl logs <pod-name> -n dev

# Previous container logs (useful after a crash/restart)
kubectl logs <pod-name> -n dev --previous

# Check events for the namespace
kubectl get events -n dev --sort-by='.lastTimestamp'

# Exec into a running container
kubectl exec -it <pod-name> -n dev -- sh

# Check what values Helm is using for the current release
helm get values payzee -n dev

# Preview rendered templates without deploying
helm template payzee ./k8s/helm -f k8s/helm/values-override.yaml

# Lint the chart
helm lint --strict ./k8s/helm

# Release history
helm history payzee -n dev
```

## Uninstall

```bash
helm uninstall payzee -n dev
kubectl delete namespace dev

# To also remove Traefik
helm uninstall traefik -n traefik
kubectl delete namespace traefik
```
