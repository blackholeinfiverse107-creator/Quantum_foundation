# Integration Proof — AI Assistant Backend

## Endpoint
POST /api/assistant

## Sample Request

```bash
curl -X POST https://<YOUR_BACKEND_URL>/api/assistant \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <API_KEY>" \
  -d '{
    "message": "Remind me to call John tomorrow"
}'

## Expected Behavior
Returns a deterministic JSON response
Response schema remains stable
No internal system logic is exposed
Frontend can safely consume the response

## Verification
Request tested locally
Request tested on live deployment
Frontend integration confirmed