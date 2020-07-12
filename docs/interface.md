# 接口文档
<!-- TOC -->

- [接口文档](#接口文档)
    - [一、用户模块](#一用户模块)
        - [1.1 GitHub 登录](#11-github-登录)
        - [1.2 用户详情](#12-用户详情)
        - [1.3 退出登录](#13-退出登录)
    - [二、文档管理](#二文档管理)
        - [2.1 列出文档目录](#21-列出文档目录)
        - [2.2 删除文档](#22-删除文档)
        - [2.3 上传文档](#23-上传文档)
        - [2.4 查询指定文档](#24-查询指定文档)
    - [三、storage](#三storage)
        - [3.1 获得存储令牌](#31-获得存储令牌)

<!-- /TOC -->

## 一、用户模块

### 1.1 GitHub 登录

* 请求URL
```sh
(GET) http(https)://host/webapi/user/github_login
```
* 接口参数: 无
* 接口返回: 重定向至 GitHub OAuth 登录授权页

### 1.2 用户详情

* 请求URL
```sh
(GET) http(https)://host/webapi/user/
(GET) http(https)://host/webapi/user/profile
```
* 接口参数: 无
* 接口返回: 
```sh
{
    "success":true,
    "data":{
        "cred": "GUEST",                # 用户身份，GUEST - 访客，USER - 用户，ADMIN - 管理员
        "uid": "xxxx",                  # 用户id
        "nickname": "xxxx",             # 用户昵称
        "avatar": "xxxx",               # 用户头像
        "create_time": "2020-05-31 12:58:42",
        "update_time": "2020-05-31 12:59:20",
    }
}
```

### 1.3 退出登录
```sh
(GET) http(https)://host/webapi/user/logout
```
* 接口参数: 无

参数名|类型|是否必填|描述
-|-|-|-
login_scene|string|必填|登录场景标识，前端随机生成的字符串。后续要用该标识校验用户是否登录。

* 接口返回: 
```json
{
    "success":true
}
```

## 二、文档管理

### 2.1 列出文档目录

```sh
(GET) http(https)://host/webapi/doc/list
```
* 接口参数: 

参数名|类型|是否必填|描述
-|-|-|-
creator|string|选填|列出指定用户创建的文档，未填时列出所有用户文档。
status|string|选填|列出指定状态的文档，未填时列出所有状态文档。WAIT - 文档生成中, SUCCESS - 文档生成完成，FAILED - 文档生成失败


* 接口返回: 
```sh
{
  "success": true,
  "data": {
    "start": 0,
    "limit": 20,
    "total": 1,
    "items": [
      {
        "doc_id": "3e2e675c-ab14-4635-adc5-2cf1b2f29852",
        "creator": {
          "uid": "aa0abdd5-4d5a-460d-b3ca-8a70e27469d7",
          "github_id": "13912637",
          "cred": "USER",
          "nickname": "lsj9383",
          "avatar": "https://avatars2.githubusercontent.com/u/13912637?v=4",
          "create_time": "2020-07-11 17:56:17",
          "update_time": "2020-07-11 17:56:17"
        },
        "title": "test",
        "desc": "testdesc",
        "source": "1.zip",
        "url": "",
        "progress": 0,
        "status": "WAIT",
        "create_time": "2020-07-11 20:52:20",
        "update_time": "2020-07-11 20:52:20"
      }
    ]
  }
}
```

### 2.2 删除文档
只有管理员和用户创建者可以删除文档
```sh
(GET) http(https)://host/webapi/doc/remove
```
* 接口参数: 

参数名|类型|是否必填|描述
-|-|-|-
doc_id|string|必填|文档id


* 接口返回: 
```json
{
    "success":true
}
```

### 2.3 上传文档

```sh
(GET) http(https)://host/webapi/doc/post
```
* 接口参数: 

参数名|类型|是否必填|描述
-|-|-|-
title|string|必填|文档标题
source|string|必填|文档源, 目前仅支持 zip 压缩包。
desc|string|选填|文档描述


* 接口返回: 
```json
{
    "success":true,
    "data": {"doc_id": "xxxxx"}
}
```

### 2.4 查询指定文档
```sh
(GET) http(https)://host/webapi/doc/query
```
* 接口参数: 

参数名|类型|是否必填|描述
-|-|-|-
doc_id|string|必填|文档id

* 接口返回: 
```sh
{
    "success":true,
    "data": {
        "doc_id": "xxxx",
        "title": "xxxx",
        "desc": "xxxx",
        "url":"xxxx",
        "source": "xxxxx",
        "progress": 10,         # 文档生成进度
        "status": "SUCCESS",
        "creator": {"uid": "xxxxx", "nickname": "xxxxx", "avatar": "xxxxx"},
        "create_time": "2020-05-31 12:58:42",
        "update_time": "2020-05-31 12:59:20",
    }
}
```

## 三、storage

### 3.1 获得存储令牌
```sh
(GET) http(https)://host/webapi/storage/token
```

* 接口参数:

参数名|类型|是否必填|描述
-|-|-|-
path|str|选填|文件的存放相对路径（相对于 `/user/${uid}` 而言）

* 请求响应：

```json
{
  "success": true,
  "data": {
    "token": "sRd2-QgwgZnPgZyY1E6oS0QxtFWjGLNJwss9D2Op:v_WE5CLhvtODk3e2TkPK1wnmkrg=:eyJzY29wZSI6InRyYWRlLXdvcmtmbG93Oi91aWRfMC8iLCJkZWFkbGluZSI6MTU5MDgzMjA3M30=",
    "path": "/user/${uid}/${path}"
  }
}
```
