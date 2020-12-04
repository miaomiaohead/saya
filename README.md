# saya
Online RST doc platform

```sh
# 生成不带任何第三方包的虚拟环境, 名字为venv
$ virtualenv --no-site-packages venv

# 进入虚拟环境
$ source venv/bin/activate

# 安装依赖项
(venv)$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 退出虚拟环境
(venv)$ deactivate
```

字段|类型|必填|描述
-|-|:-:|-
Authorization|string|Y|Web API 访问令牌，格式为 `bearer ACCESS_TOKEN`，[access_token]() 的获取请参考请求访问令牌。
Content-Type|string|Y|固定为 `application/json;charset=utf-8`。

```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=utf-8

{
    "result": {
        "error_code": 2230001,
        "error_message": "empty request."
    }
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=utf-8

{
    "result": {
        "error_code": 2230001,
        "error_message": "empty request."
    }
}
```
