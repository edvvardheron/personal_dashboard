from fastapi import FastAPI

app = FastAPI(title='fastapi trial', description='trialling the FastAPI framework.', version='1.0.0')

#we can GET, PUT, POST, DELETE, PATCH, OPTIONS, HEAD, TRACE, CONNECT

@app.get("/")
async def read_root():
    return {'message': 'Hello, World!'}
