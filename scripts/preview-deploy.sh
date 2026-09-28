#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"

require_pr "${1:-}"
pr="$1"
sha="${2:-$(git rev-parse --short HEAD)}"
tag="sha-$sha"
ns="$(namespace "$pr")"
url="$(preview_url "$pr")"

docker build -q -t "preview-api:$tag" "$ROOT/apps/api"
docker build -q -t "preview-web:$tag" "$ROOT/apps/web"
k3d image import "preview-api:$tag" "preview-web:$tag" --cluster "$CLUSTER"

kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "$ns" "preview.pr=$pr" --overwrite

helm upgrade --install preview "$ROOT/charts/preview-app" \
  --namespace "$ns" \
  --set pr="$pr" \
  --set commit="$sha" \
  --set domain="$DOMAIN" \
  --set port="$PORT" \
  --set web.image.tag="$tag" \
  --set api.image.tag="$tag" \
  --wait --timeout 3m

# The pods are ready before Traefik has picked up the new host, so poll the
# ingress until it actually serves the app.
for _ in $(seq 60); do
  if curl -fs -o /dev/null --max-time 5 "$url/api/healthz"; then
    echo "$url"
    exit 0
  fi
  sleep 2
done

echo "ingress did not answer at $url" >&2
kubectl -n "$ns" get pods,ingress >&2
exit 1
