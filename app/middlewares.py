from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
#     origins = [
#     "https://omars-macbook-air.tail1f6871.ts.net:8443/",
    
#     "https://localhost:3000",  
#    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    
