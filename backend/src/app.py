import uvicorn

import backend.startup  # pylint: disable=W0611
import backend.routes  # pylint: disable=W0611

if __name__ == "__main__":
    uvicorn.run("app:app",
                host="127.0.0.1",
                port=1337,
                log_level="info",
                reload=True)
