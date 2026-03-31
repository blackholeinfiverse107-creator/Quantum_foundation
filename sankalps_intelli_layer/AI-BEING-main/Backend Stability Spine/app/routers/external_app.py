from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# FIXED IMPORT ✔
from ..core.external_integrations import ExternalIntegrations

router = APIRouter()

class AppRequest(BaseModel):
    app: str  # notion, googlesheets, trello, email, webhook
    action: str
    params: dict = {}

integrations = ExternalIntegrations()

@router.post("/external_app")
async def interact_external_app(request: AppRequest):
    try:
        if request.app == 'email':
            if request.action in ['send_email', 'send']:
                to_email = request.params.get("to_email", "test@example.com")
                result = {"status": "success", "email_action": request.action, "to": to_email}
                return {"result": result}
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Email")

        # Mocked apps handled without integration
        if request.app in ['crm', 'erp', 'calendar']:
            if request.app == 'crm':
                result = {"crm_action": request.action, "status": "success"}
            elif request.app == 'erp':
                result = {"erp_action": request.action, "status": "success"}
            else:
                result = {"calendar_action": request.action, "status": "success"}
            return {"result": result}

        integration = integrations.get_integration(request.app)

        if request.app == 'notion':
            if request.action == 'create_page':
                result = integration.create_page(**request.params)
            elif request.action == 'update_page':
                result = integration.update_page(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Notion")

        elif request.app == 'googlesheets':
            if request.action == 'append_row':
                result = integration.append_row(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for GoogleSheets")

        elif request.app == 'trello':
            if request.action == 'create_card':
                result = integration.create_card(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Trello")

        elif request.app == 'webhook':
            if request.action == 'post':
                result = integration.post_webhook(**request.params)
            else:
                raise HTTPException(status_code=400, detail=f"Invalid action '{request.action}' for Webhook")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported app '{request.app}'")

        return {"result": result}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration error: {str(e)}")
