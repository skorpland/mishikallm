#!/bin/sh

if [ "$USE_DDTRACE" = "true" ]; then
    export DD_TRACE_OPENAI_ENABLED="False"
    exec ddtrace-run mishikallm "$@"
else
    exec mishikallm "$@"
fi