import docker 
import os 

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

def get_ports(container):
    ports = []
    try:
        list_ports = list(container.ports.keys())
        for port_key in list_ports:
            for port_obj in container.ports[port_key]:
                ports.append(port_obj['HostPort'])
    except:
        pass

    return ports

@app.get("/")
def read_root(request: Request, sortstatus: str = '', sortports: str = '', sortindex: str = '', sortname: str = ''):

    client = docker.from_env()
    # print(client)

    containers = client.containers.list(all=True)
    containers = sorted(containers, key=lambda x: x.name)

    containers_result = []
    for index, container in enumerate(containers):
        containers_result.append({
            "index": index+1,
            "id": container.id,
            "ip": os.environ.get('EXTERNAL_IP'),
            "name": container.name,
            "status": container.status,
            "ports": get_ports(container),
        })

    if sortindex != '':
        containers_result = sorted(containers_result, key=lambda x: x["index"], reverse=(sortindex=='down'))

    if sortname != '':
        containers_result = sorted(containers_result, key=lambda x: x["name"], reverse=(sortname=='down'))

    if sortstatus != '':
        containers_result = sorted(containers_result, key=lambda x: x["status"], reverse=(sortstatus=='down'))

    if sortports != '':
        containers_result = sorted(containers_result, key=lambda x: x["ports"], reverse=(sortports=='down'))

    return templates.TemplateResponse('index.html', {"request": request, "containers": containers_result})


@app.get("/docker/")
async def docker_action(name: str = '', action: str = '', command: str = ''):
    message = 'success'

    try:
        client = docker.from_env()
        container = client.containers.get(name)
        if action == 'start':
            container.start()
        elif action == 'stop':
            container.stop()
        elif action == 'logs':
            message = container.logs(tail=60, stream=True, follow=False)
            message = list(message)[::-1]
            message = b''.join(message)
        elif action == 'restart':
            message = container.restart()
        elif action == 'exec':
            message = container.exec_run(cmd=command.split(' '))
        else:
            raise HTTPException(status_code=400, detail='Invalid action')
    except docker.errors.NotFound as e:
        raise HTTPException(status_code=404, detail='Container not found')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Error performing action')

    return {'message': message}
