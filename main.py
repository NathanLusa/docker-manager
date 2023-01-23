import docker 

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

@app.get("/")
def read_root(request: Request):

    client = docker.from_env()
    containers = client.containers.list(all=True)

    containers_result = []
    for index, container in enumerate(containers):
        containers_result.append({
            "index": index+1,
            "id": container.id,
            "name": container.name,
            "logs": container.logs(),
        })

    return templates.TemplateResponse('index.html', {"request": request, "containers": containers_result})
    # return {"containers": containers_result}


# class DockerAction(BaseModel):
#     name: str
#     action: str


@app.get("/docker/")
async def docker_action(name: str = '', action: str = '', command: str = ''):
    # name = docker_data.name
    # action = docker_data.action
    message = 'success'

    try:
        client = docker.from_env()
        container = client.containers.get(name)
        if action == 'start':
            container.start()
        elif action == 'stop':
            container.stop()
        elif action == 'logs':
            message = container.logs()
        elif action == 'restart':
            message = container.restart()
        elif action == 'exec':
            message = container.exec_run(cmd=command.split(' '))
        else:
            raise HTTPException(status_code=400, detail='Invalid action')
    except docker.errors.NotFound as e:
        raise HTTPException(status_code=404, detail='Container not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Error performing action')

    return {'message': message}
