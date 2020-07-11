# -*- coding:utf-8 -*-

import uuid

from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import *
from SpiffWorkflow.operators import *
from SpiffWorkflow.task import Task
from trade_flow_specs import TradeFlowSerializer


def workflow_skip_start_and_root(workflow):
    while True:
        ready_tasks = workflow.get_tasks(Task.READY)
        finish = True
        for t in ready_tasks:
            if isinstance(t.task_spec, StartTask) or t.task_spec.name == "Root":
                t.complete()
                finish = False
            if finish:
                return


def init_workflow_from_spec_json(spec_json):
    serializer = TradeFlowSerializer()
    spec = WorkflowSpec.deserialize(serializer, spec_json)

    workflow = Workflow(spec)
    workflow_meta = {"id": str(uuid.uuid4()), "fields": []}

    workflow_skip_start_and_root(workflow)

    for t in workflow.get_tasks():
        t.task_spec.x_instances = []

    for t in workflow.get_tasks():
        if "_meta" not in t.task_spec.data:
            t.task_spec.data["_meta"] = {}
        if not isinstance(t.task_spec.data["_meta"], dict):
            t.task_spec.data["_meta"] = {}

        t.task_spec.data["_meta"]["locked"] = False
        t.task_spec.data["_meta"]["id"] = str(t.id)
        t.task_spec.data["_meta"]["type"] = t.task_spec.__class__.__name__
        # workflow_meta["fields"] += t.task_spec.data["_meta"].get("fields", [])

    workflow.data["_meta"] = workflow_meta
    return workflow


def workflow_json_serialize(workflow):
    serializer = TradeFlowSerializer()
    workflow_json = workflow.serialize(serializer)
    return workflow_json


def workflow_deserialize(workflow_json):
    serializer = TradeFlowSerializer()
    workflow_instance = Workflow.deserialize(serializer, workflow_json)
    return workflow_instance


def get_workflow_id(workflow):
    return workflow.data["_meta"]["id"]


def get_ready_tasks(workflow):
    return workflow.get_tasks(Task.READY)


def cancel_workflow(workflow_instance):
    workflow_instance.cancel()


def sync_data(task, data, keep_status):
    """将数据进行同步，只对完成或就绪的 task 及其 children 有效
    """
    old_state = task.state
    task.data.update(data)

    # 如果需要保持状态，则不不对当前 Task 完成
    if not keep_status:
        task.complete()

    # 如果之前的状态就是 READY 则直接返回，否则将数据传递给后续的 Task
    if old_state == Task.READY:
        return True

    def _inner(children):
        for child in children:
            if child.state == Task.COMPLETED or child.state == Task.READY:
                child.data.update(data)
                _inner(child.children)
        return True
    return _inner(task.children)


def get_task_state_name(task):
    return Task.state_names[task.state]


def get_task_meta(task):
    return task.task_spec.data.get("_meta", {})


def get_task_data(task):
    return task.data


def get_task_fields(task):
    return get_task_meta(task).get("fields", [])


def get_task_prev_handlers(task):
    return get_task_meta(task).get("prev_handlers", [])


def get_task_post_handlers(task):
    return get_task_meta(task).get("post_handlers", [])


def get_task(workflow, task_id):
    for t in workflow.get_tasks():
        if task_id == str(t.id):
            return t
    return None


def get_task_id(task):
    return str(task.id)


def is_task_locked(task):
    return get_task_meta(task).get("locked")


def get_task_viewer(task):
    meta = task.task_spec.data.get("_meta")
    if not meta or not isinstance(meta, dict):
        return None
    return meta.get("viewer")


def get_task_committer(task):
    meta = task.task_spec.data.get("_meta")
    if not meta or not isinstance(meta, dict):
        return None
    return meta.get("committer", {})


def get_task_parent(task):
    parent = [inp.data.get("_meta", {}).get("id") for inp in task.task_spec.inputs]
    if not parent and task.parent:
        # 如果通过 task_spec 的 inputs 得到的 parent 为空，则直接获取任务的 parent
        # 主要是针对 Spiffworkflow 没有处理 Root 和 Start 的父子关系的情况
        parent = [str(task.parent.id)]
    return parent


def get_task_children(task):
    return [str(c.id) for c in task.children]


def get_task_chain(workflow_instance):
    task_chain = []
    for t in workflow_instance.get_tasks():
        task_chain.append({
            "task_id": str(t.id),
            "task_name": t.task_spec.name,
            "task_state": Task.state_names[t.state],
            "task_type": t.task_spec.__class__.__name__,
            "task_fields": t.task_spec.data["_meta"].get("fields", []),
            "parent": get_task_parent(t),
            "children": get_task_children(t),
        })
    return task_chain


def lock_task_parent_chain(task):
    """将所有的父节点上锁
    """
    def inner(inputs):
        for inp in inputs:
            meta = inp.data.get("_meta", {})
            if isinstance(meta, dict):
                meta["locked"] = True
            inner(inp.inputs)
    inner(task.task_spec.inputs)
