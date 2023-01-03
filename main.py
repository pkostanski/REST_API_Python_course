from fastapi import FastAPI


app = FastAPI()

@app.get("/", tags=["category1"])
def read_root():
    return {"Hello": "from root1"}

@app.get("/root2", tags=["category2"])
def read_root2():
    """This endpoint is for test only"""
    return {"Hello": "from root2"}