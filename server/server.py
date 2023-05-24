import asyncio
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QFile
from PyQt5.uic import loadUi

USERS = {}
ADDRESS = "0.0.0.0"
PORT = 1404

class ServerThread(QThread):

    messageReceived = pyqtSignal(str)
    usersUpdated = pyqtSignal(list)

    async def handle_client(self, reader, writer):
        while True:

            data = json.loads((await reader.read(8192)).decode())

            if data["code"] == "nick":
                nickname = data["message"]
                USERS[nickname] = [reader, writer]
                self.messageReceived.emit(f'{data["from"]} HAS CONNECTED')
                self.usersUpdated.emit(list(USERS.keys()))
            
            if data["code"] == "exit":
                self.messageReceived.emit(f'{data["from"]} HAS DISCONNECTED')

                writer.close()
                USERS.pop(data["from"])

                self.usersUpdated.emit(list(USERS.keys()))
                break
            
            if data["code"] == "find":
                test = USERS.get(data["message"])
                if test is not None:
                    dict_send = {
                        "code": "user",
                        "from": "server",
                        "to": data["from"],
                        "message": data["message"]
                    }
                else:
                    dict_send = {
                        "code": "error",
                        "from": "server",
                        "to": data["from"],
                        "message": f"No user with name {data['message']}"
                    }
                await self.send(dict_send)
            
            if data["code"] == "send":
                dict_send = {
                    "code": "receive",
                    "from": data["from"],
                    "to": data["to"],
                    "message": data["message"]
                }
                await self.send(dict_send)
                self.messageReceived.emit(
                    f'{data["from"]} SEND MESSAGE TO {data["to"]}'
                )

    async def send(self, data: dict) -> None:
        receiver = USERS[data["to"]][1]
        receiver.write(json.dumps(data).encode())
        await receiver.drain()

    async def run_server(self):
        server = await asyncio.start_server(self.handle_client, ADDRESS, PORT)
        print("Server started")
        async with server:
            await server.serve_forever()

    def run(self):
        asyncio.run(self.run_server())


class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = QFile("server.ui")
        ui_file.open(QFile.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()

    def display_message(self, message):
        self.text_edit.append(message)

    def update_user_list(self, users):
        self.user_list.clear()
        self.user_list.addItems(users)

if __name__ == "__main__":
    app = QApplication([])
    window = ServerWindow()
    window.show()

    server_thread = ServerThread()
    server_thread.messageReceived.connect(window.display_message)
    server_thread.usersUpdated.connect(window.update_user_list)
    server_thread.start()

    app.exec_()