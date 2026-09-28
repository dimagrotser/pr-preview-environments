{{- define "preview.pr" -}}
{{- required "pr is required: helm ... --set pr=<number>" .Values.pr | toString -}}
{{- end -}}

{{- define "preview.host" -}}
pr-{{ include "preview.pr" . }}.{{ .Values.domain }}
{{- end -}}

{{- define "preview.labels" -}}
app.kubernetes.io/name: preview-app
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
preview.pr: {{ include "preview.pr" . | quote }}
{{- end -}}
