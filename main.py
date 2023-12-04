import docker 
import os 

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

def get_container_list() -> []:
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
    
    return containers_result


def get_image_list() -> []:
    client = docker.from_env()
    # print(client)

    images = client.images.list(all=True)
    # images = sorted(images, key=lambda x: x.name)

    images_result = []
    for index, image in enumerate(images):
        images_result.append({
            "index": index+1,
            "id": image.id,
            # "ip": os.environ.get('EXTERNAL_IP'),
            "name": image.attrs['RepoTags'][0].split(':')[0] if len(image.attrs['RepoTags']) > 0 else '',
            "fullname": image.attrs['RepoTags'][0] if len(image.attrs['RepoTags']) > 0 else '',
            # "status": image.status,
            # "ports": get_ports(image),
        })
    
    return images_result


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

    containers = get_container_list()
    images = get_image_list()

    if sortindex != '':
        containers = sorted(containers, key=lambda x: x["index"], reverse=(sortindex=='down'))

    if sortname != '':
        containers = sorted(containers, key=lambda x: x["name"], reverse=(sortname=='down'))

    if sortstatus != '':
        containers = sorted(containers, key=lambda x: x["status"], reverse=(sortstatus=='down'))

    if sortports != '':
        containers = sorted(containers, key=lambda x: x["ports"], reverse=(sortports=='down'))

    return templates.TemplateResponse('index.html', {"request": request, "containers": containers, "images": images})


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
        elif action == 'remove':
            message = container.remove()
        elif action == 'exec':
            message = container.exec_run(cmd=command.split(' '))
        else:
            raise HTTPException(status_code=400, detail='Invalid action')
    except docker.errors.NotFound as e:
        raise HTTPException(status_code=404, detail='Container not found')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='Error performing action')

    return {'detail': message}



@app.get("/images/")
async def image_action(name: str = '', action: str = ''):
    message = 'success'

    try:
        client = docker.from_env()
        # container = client.images.get(name)
        if action == 'remove':
            client.images.remove(name)
        else:
            raise HTTPException(status_code=400, detail='Invalid action')
    except docker.errors.NotFound as e:
        raise HTTPException(status_code=404, detail='Image not found')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f'Error performing action. \n{e}')

    return {'detail': message}
