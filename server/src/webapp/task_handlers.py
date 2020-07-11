# -*- coding:utf-8 -*-

"""
任务处理器接口:
error_message = handler(request_data, task_data)
"""

from webapp import proto
from webapp.service import user_service


def test_new_task_prev_handler(request_data, task_data):
    print("=============== prev handler ===============")
    print("request_data:", request_data)
    print("task_data:", task_data)


def test_new_task_post_handler(request_data, task_data):
    print("=============== post handler ===============")
    print("request_data:", request_data)
    print("task_data:", task_data)


def register_insert_user(request_data, task_data):
    """进入审核时将用户入库
    """
    uid = task_data["session.uid"]
    phone = task_data["phone"]
    email = task_data["email"]
    password = task_data["password"]
    if not uid or not phone or not email or not password:
        return "uid or phone or email or password empty"
    user_service.insert_user_with_roles(uid, phone, email, password, roles=[proto.EnumRole.GUEST])


def register_on_confirm(request_data, task_data):
    """审核通过改变角色为 USER
    """
    if not request_data.get("confirm"):
        return
    uid = task_data["session.uid"]
    user_service.replace_user_roles(uid, roles=[proto.EnumRole.USER])


def update_corp_on_confirm(request_data, task_data):
    """审核通过改变角色为 USER
    """
    if not request_data.get("confirm"):
        return
    roles = user_service.query_user_roles()
    if proto.EnumRole.GUEST not in roles:
        return
    roles.remove(proto.EnumRole.GUEST)
    roles.add(proto.EnumRole.USER)
    uid = task_data["session.uid"]
    user_service.replace_user_roles(uid, roles=roles)


mapper = {
    "test.new_task_prev_handler": test_new_task_prev_handler,
    "test.new_task_post_handler": test_new_task_post_handler,
    "register.insert_user": register_insert_user,
    "register.on_confirm": register_on_confirm,
    "update_corp.on_confirm": update_corp_on_confirm,
}
