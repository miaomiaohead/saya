# install dependency
FROM python:3.6 AS build

COPY requirements.txt /usr/requirements.txt

RUN pip install -r /usr/requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --prefix=/usr/install

# construct runtime
FROM python:3.6-alpine

COPY --from=build /usr/install /usr/local/
COPY src /usr/python_server_src

WORKDIR /usr/python_server_src

CMD python entry.py
