import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="PetLet-PMS-Agent-Gateway")

# --- SCHEMAS (Structured Outputs for the AI) ---
class BookingUpdate(BaseModel):
    booking_id: str = Field(..., description="The unique ID of the guest reservation")
    new_checkout_date: str = Field(..., description="ISO format date for the requested extension")
    reason: Optional[str] = Field(None, description="Reason for the check-out modification")

# --- PMS API CLIENT (Logic Layer) ---
class PMSService:
    def __init__(self):
        self.base_url = "https://api.pms-provider.com/v1"
        self.headers = {"Authorization": f"Bearer {os.getenv('PMS_API_KEY')}"}

    async def extend_stay(self, data: BookingUpdate):
        # In a real scenario, this is where you read documentation 
        # and write the specific REST integration
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/bookings/{data.booking_id}",
                json={"checkout_date": data.new_checkout_date},
                headers=self.headers
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="PMS Update Failed")
            return response.json()

# --- TOOL ENDPOINTS (Exposed to AI Agent) ---
@app.post("/tools/extend-checkout")
async def tool_extend_checkout(payload: BookingUpdate, service: PMSService = Depends()):
    """
    Agentic Tool: Allows the AI to modify booking check-out dates 
    autonomously based on guest requests and calendar availability.
    """
    result = await service.extend_stay(payload)
    return {"status": "success", "agent_action": "checkout_extended", "data": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
