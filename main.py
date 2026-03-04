import os
import httpx
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables (API Keys, etc.)
load_dotenv()

# Setup logging for Agent Observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PetLet-Agent-Gateway")

app = FastAPI(
    title="Pet Let AI Agent Gateway",
    description="Custom Tool-Server for autonomous Property Management actions.",
    version="1.0.0"
)

# --- SCHEMAS (Defines how the AI MUST talk to our system) ---
class BookingUpdate(BaseModel):
    booking_id: str = Field(..., description="The unique ID of the reservation in the PMS")
    new_checkout_date: str = Field(..., description="Target checkout date in ISO 8601 format (YYYY-MM-DD)")
    reason: Optional[str] = Field(None, description="The reason provided by the guest for the extension")

# --- LOGIC LAYER (The engine that talks to the PMS) ---
class PMSService:
    def __init__(self):
        # These would be the actual credentials for Pet Let's systems
        self.base_url = os.getenv("PMS_API_URL", "https://api.pms-provider.com/v1")
        self.api_key = os.getenv("PMS_API_KEY")

    async def extend_stay(self, data: BookingUpdate) -> Dict[str, Any]:
        """Communicates with the PMS to modify booking state."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # In production, we'd first check availability before patching
                response = await client.patch(
                    f"{self.base_url}/bookings/{data.booking_id}",
                    json={"checkout_at": data.new_checkout_date},
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 401:
                    logger.error("Authentication failed with PMS API.")
                    raise HTTPException(status_code=500, detail="Backend Auth Failure")
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"PMS API Error: {e.response.text}")
                raise HTTPException(status_code=e.response.status_code, detail="PMS sync failed")
            except Exception as e:
                logger.error(f"Unexpected System Error: {str(e)}")
                raise HTTPException(status_code=500, detail="Internal Server Error during action")

# --- TOOL ENDPOINTS (Exposed for LLM Function Calling) ---
@app.post("/tools/extend-checkout")
async def tool_extend_checkout(payload: BookingUpdate, service: PMSService = Depends()):
    """
    AGENTIC TOOL: Closes the loop on late checkout requests.
    Validates the request, checks logic, and executes the state change in the PMS.
    """
    logger.info(f"Agent triggered 'extend-checkout' for Booking {payload.booking_id}")
    
    # Execute the action
    result = await service.extend_stay(payload)
    
    return {
        "status": "success",
        "agent_action": "modify_booking_checkout",
        "observation": f"Booking {payload.booking_id} was successfully updated to {payload.new_checkout_date}.",
        "pms_response": result
    }

@app.get("/health")
async def health_check():
    return {"status": "online", "environment": "Production-Linux-Zorin"}

if __name__ == "__main__":
    import uvicorn
    # Entry point for local development
    uvicorn.run(app, host="0.0.0.0", port=8000)
