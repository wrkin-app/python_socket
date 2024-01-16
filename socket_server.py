import asyncio
import websockets
import json

import os
import django
from datetime import datetime
from django.conf import settings


# Set up Django without a project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Add this line

django.setup()

from socket_app.models import *

rooms = {}

async def echo(wss, path):
    
    if path == '/chatRoom':
        try:
            async for message in wss:
                data = json.loads(message)
                print(data)
                room_id = data['room_id']
                user_id = data['user_id']  
                action_type = data['action_type']
                # action_type = 'join'
                if action_type == 'join':     
                    pre_exist_room_id_flag = rooms.get(room_id,False)
                    if not pre_exist_room_id_flag:
                        rooms[room_id] = [[user_id,wss]]
                    else:
                        pre_exist_user_flag = False
                        for user in rooms[room_id]:
                            if user[0] == user_id:
                                pre_exist_user_flag = True
                                user[1] = wss
                                break 
                        if not pre_exist_user_flag:
                            rooms[room_id].append([user_id,wss])
                    send_data = {'status':True,'message':'socket connected'}
                    send_data = json.dumps(send_data)
                    # await wss.send(str(send_data))
                    print('joinnnn',rooms)
                elif action_type == 'send_message':
                    message_data = data['message_data']
                    message_type =  message_data['type']
                    print("message_data",message_data)
                    current_datetime = datetime.now()
                    if message_type == 'message':
                        print('chat started')
                        chat_obj = Chats(
                                            room_id = int(room_id),
                                            user_id = int(user_id),
                                            message = message_data['message'],
                                            is_enabled = True,
                                            is_task = False,
                                            created_at = current_datetime,
                                        )
                        chat_obj.save()
                        print('chat mid')
                        send_data = {
                                        "id": chat_obj.id,
                                        "user_id": chat_obj.user_id,
                                        "name":chat_obj.user.name,
                                        "is_task": False,
                                        "message": {
                                            "text": chat_obj.message,
                                            "is_media": False,
                                            "media": {}
                                        },
                                        "task": {},
                                        "sent_time": chat_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                        "reply": {}
                                    }  
                        print('chat ended')
                    elif message_type == 'task':
                        task_data = message_data['task']
                        task_obj = Task(
                                            title = task_data['title'],
                                            description = task_data['description'],
                                            from_user_id = task_data['from_user'],
                                            to_user_id = task_data['to_user'],
                                            start_date = task_data['start'],
                                            end_date = task_data['end'],
                                            priority = task_data['priority'],
                                            status = 'pending',
                                        )
                        task_obj.save()
                        chat_obj = Chats(
                                            room_id = room_id,
                                            user_id = user_id,
                                            is_enabled = True,
                                            is_task = True,
                                            task_id = task_obj.id,
                                            created_at = current_datetime,
                                        )
                        chat_obj.save()
                        send_data = {
                                        "id": chat_obj.id,
                                        "user_id": chat_obj.user,
                                        "is_task": True,
                                        "message": {},
                                        "task": {
                                                    "id": task_obj.id,
                                                    "title": task_obj.title,
                                                    "description": task_obj.description,
                                                    "from_user": task_obj.from_user_id,
                                                    "to_user": task_obj.to_user_id,
                                                    "start_date": task_obj.start_date,
                                                    "end_date": task_obj.end_date,
                                                    "priority": task_obj.priority
                                        },
                                        "sent_time": chat_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                        "reply": {}
                                    } 
                    print("send_data",send_data)
                    send_data = json.dumps(send_data)
                    print("send data casted")
                    print(rooms)
                    for user in rooms[room_id]:
                        print('userrrrr',user)
                        await user[1].send(str(send_data))
                    # await wss.send(str(send_data))
        except:
            pass
        finally:
            pre_exist_room_id_flag = rooms.get(room_id,False)
            if pre_exist_room_id_flag:
                for index,user in enumerate(rooms[room_id]):
                    if user[0] == user_id:
                        break
                rooms[room_id].pop(index)
                if not rooms[room_id]:
                    rooms.pop(room_id)
            print(f"Client disconnected: {wss}")
            print('disc',rooms)


async def main():
    server = await websockets.serve(echo, "0.0.0.0", 8001)
    print("WebSocket server started on ws://0.0.0.0:8001")

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())