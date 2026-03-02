{{/*
Expand the name of the chart.
*/}}
{{- define "payzee.name" -}}
{{- .Chart.Name }}
{{- end }}

{{/*
Create a fully qualified name: <release>-<chart>, truncated to 63 chars.
If the release name already contains the chart name, use the release name only.
*/}}
{{- define "payzee.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels applied to every resource.
*/}}
{{- define "payzee.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "payzee.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels (stable subset used in matchLabels — never add mutable fields here).
*/}}
{{- define "payzee.selectorLabels" -}}
app.kubernetes.io/name: {{ include "payzee.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
