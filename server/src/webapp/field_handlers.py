# -*- coding:utf-8 -*-

"""
任务处理器接口:
error_message = handler(field_name, request_data, task_data)
"""

from webapp.share import session_helper
from webapp.service import user_service


def common_inject_session_uid(field_name, request_data, task_data):
    uid = session_helper.get_uid()
    request_data[field_name] = uid


def common_unique_email_verify(field_name, request_data, task_data):
    email = request_data.get(field_name)
    if not email:
        email = task_data.get(field_name)

    exists = user_service.users_exists_email(email)
    if exists:
        return "邮箱已存在"


def common_unique_phone_verify(field_name, request_data, task_data):
    phone = request_data.get(field_name)
    if not phone:
        phone = task_data.get(field_name)

    exists = user_service.users_exists_phone(phone)
    if exists:
        return "手机已存在"


mapper = {
    "common.inject_session_uid": common_inject_session_uid,
    "common.unique_phone_verify": common_unique_phone_verify,
    "common.unique_email_verify": common_unique_email_verify,
}
