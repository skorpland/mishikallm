from mangum import Mangum
from mishikallm.proxy.proxy_server import app

handler = Mangum(app, lifespan="on")
