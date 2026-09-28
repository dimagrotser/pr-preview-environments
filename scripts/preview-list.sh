#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"

reap=false
[[ "${1:-}" == "--reap" ]] && reap=true

prs="$(kubectl get namespace -l preview.pr -o jsonpath='{range .items[*]}{.metadata.labels.preview\.pr}{"\n"}{end}' | sort -n)"

if [[ -z "$prs" ]]; then
  echo "no preview environments"
  exit 0
fi

for pr in $prs; do
  age="$(kubectl get namespace "$(namespace "$pr")" -o jsonpath='{.metadata.creationTimestamp}')"
  state="$(gh pr view "$pr" --json state --jq .state 2>/dev/null || echo UNKNOWN)"
  printf '%-8s %-8s %s  %s\n' "PR #$pr" "$state" "$age" "$(preview_url "$pr")"

  if $reap && [[ "$state" != "OPEN" && "$state" != "UNKNOWN" ]]; then
    "$(dirname "$0")/preview-destroy.sh" "$pr"
  fi
done
