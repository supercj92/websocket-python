#-*- encoding:utf-8 -*-
import tornado.web, tornado.websocket
import tornado.httpserver
import tornado.ioloop
import os
import json
from tornado.options import define, options

valid_user_dict = {'weichao': 'weichao',
                   'chenchen6': 'chenchen6',
                   'xuzongpeng': 'xuzongpeng',
                   'liuwentong1': 'liuwentong1',
                   'jiaou': 'jiaou',
                   'chenjun': 'chenjun',
                   'panglijun': 'panglijun',
                   'yangke1': 'yangke1',
                   'liuyuqin': 'liuyuqin',
                   'longcangjian1': 'longcangjian1'}
define("port", default=9000, help="run on the given port", type=int)

class SocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}
    client_id_to_num_map = {}

    def open(self):
        self.write_message({'type': 'sys', 'msg': 'hello, Welcome to WebSocket'})
        #有新人加入时进行广播通知
        client_id = id(self)
        SocketHandler.clients[client_id] = self


    @staticmethod
    def send_to_all(message):
        for c in SocketHandler.clients:
            c.write_message(message)

    def on_close(self):
        uid = id(self)
        u_number = SocketHandler.client_id_to_num_map[uid]
        if uid in SocketHandler.client_id_to_num_map:
            del SocketHandler.client_id_to_num_map[uid]
        if uid in SocketHandler.clients:
            del SocketHandler.clients[uid]
        for friend_client_id in SocketHandler.clients.keys():
            SocketHandler.send_broadcast_msg(u_number, friend_client_id, 'offline')

    def update_client(self, client_id, client_number):
        for k, v in SocketHandler.client_id_to_num_map.items():
            if v == client_number:
                del SocketHandler.client_id_to_num_map[k]
        SocketHandler.client_id_to_num_map[client_id] = client_number

    @staticmethod
    def send_broadcast_msg(from_client_number, to_client_id, msg_type):
        msg_object = {'type': msg_type, 'from_client_number': from_client_number}
        if to_client_id in SocketHandler.clients:
            SocketHandler.clients[to_client_id].write_message(msg_object)

    def on_message(self, message):
        """
        {'type': 'init', 'client_number': 22} 表示是初始化的消息
        {'from': 22, 'to': 33, 'message': 'xxx'} 表示需要转发的消息
        :param message:
        :return:
        """
        client_id = id(self)
        initJson = json.loads(message)
        if u'type' in initJson and initJson[u'type'] == u'init':
            client_number = initJson[u'client_number']
            self.update_client(client_id, client_number)
            for friend_client_id in SocketHandler.clients.keys():
                if friend_client_id != client_id:
                    SocketHandler.send_broadcast_msg(client_number, friend_client_id, 'online')
        elif u'to' in initJson and u'message' in initJson:
            to_client_number = initJson[u'to']
            msg = initJson[u'message']
            from_client_id = client_id
            from_client_number = SocketHandler.client_id_to_num_map[from_client_id]
            for k, v in SocketHandler.client_id_to_num_map.items():
                if v == to_client_number:
                    SocketHandler.clients[k].write_message(json.dumps({'type': 'user', 'from_client_id': from_client_id, 'from_client_number': from_client_number, 'msg': msg}))

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('templates/index.html', user=self.current_user)

class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("username")
        self.redirect("/")


class LoginHander(BaseHandler):
    def get(self):
        self.render('templates/login.html')

    def post(self):
        user = self.get_argument("username")
        if user not in valid_user_dict:
            self.redirect('/login')
            return
        self.set_secure_cookie("username", user)
        self.redirect("/")


class GetClients(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(SocketHandler.client_id_to_num_map)

if __name__ == '__main__':
    settings = {"static_path": os.path.join(os.path.dirname(__file__), "static"),
                "cookie_secret": "vc",
                "login_url": "/login"}
    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/login', LoginHander),
        (r'/logout', LogoutHandler),
        (r'/soc', SocketHandler),
        (r'/clients', GetClients),
    ], debug=True, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
