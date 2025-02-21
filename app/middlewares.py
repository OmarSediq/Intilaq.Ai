from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    # origins = [
    #     "https://trucks-factors-derby-breed.trycloudflare.com"
    #     # "https://yourfrontenddomain.com"
    # ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
