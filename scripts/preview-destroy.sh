#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"

require_pr "${1:-}"
ns="$(namespace "$1")"

helm uninstall preview --namespace "$ns" --ignore-not-found
kubectl delete namespace "$ns" --ignore-not-found --wait
