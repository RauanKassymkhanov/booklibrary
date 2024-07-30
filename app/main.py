from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read():
    return {"message": "Welcome to the Book API"}
