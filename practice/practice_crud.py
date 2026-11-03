from datetime import datetime 

from fastapi import FastAPI, HTTPException, Request, Response

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello, World!"}


data = [
    {"campaign_id": 1, "name": "summer launch", "due_date": datetime.now(), 'created_at': datetime.now()},
    {"campaign_id": 2, "name": "Black Friday", "due_date": datetime.now(), 'created_at': datetime.now()},
]

@app.get('/campaigns')
async def get_campaigns():
    return {"campaigns": data}

@app.get('/campaigns/{campaign_id}')
async def get_campaign(campaign_id: int):
    for campaign in data:
        if campaign.get('campaign_id') == campaign_id:
            return {'campaign': campaign.get('name')}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post('/campaigns', status_code=201)
async def create_campaign(body: dict[str, str]):

    new_campaign = {
        "campaign_id": len(data) + 1,
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        'created_at': datetime.now()
    }
    data.append(new_campaign)
    return {"campaign": new_campaign}

@app.put('/campaigns/{campaign_id}')
async def update_campaign(id: int, body: dict[str, str]):

    for index, campaign in enumerate(data):
        if campaign.get('campaign_id') == id:

            updated: dict = {
                "campaign_id": id,
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                'created_at': campaign.get('created_at')
            }
            data[index] = updated
            return {"campaign": updated}
    raise HTTPException(status_code=404, detail="Campaign not found")


@app.delete('/campaigns/{campaign_id}')
async def delete_campaign(id: int):

    for index, campaign in enumerate(data):
        if campaign.get('campaign_id') == id:
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Campaign not found")