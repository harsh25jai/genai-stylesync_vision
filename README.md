# genai-stylesync_vision
Repo to create GenAI Academy APAC Prototype project

## Activate venv
```bash
source .venv/bin/activate
```

## Local Deploy
```bash
adk web --allow_origins 'regex:https://.*\.cloudshell\.dev'
```

## Local Deploy Test
```bash
uvx --from google-adk==1.14.0 adk run .
# OR
uvx --with psycopg2-binary --from google-adk==1.14.0 adk run .
# OR
uvx --with pg8000 --from google-adk==1.14.0 adk run .
```

## Load env
```bash
source .env
```

## Production Deploy
```bash
uvx --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SA_NAME \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=codelab-adk \
  --service-account=$SERVICE_ACCOUNT

# OR
uvx --with pg8000 --from google-adk==1.14.0 \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=$SA_NAME \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=codelab-adk \
  --service-account=$SERVICE_ACCOUNT
```

