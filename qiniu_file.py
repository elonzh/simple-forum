# -*- coding: utf-8 -*-
__author__ = "erliang"
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from qiniu import Auth, put_file, put_data, etag

"""
_policy_fields = set([
    "callbackUrl",
    "callbackBody",
    "callbackHost",
    "callbackBodyType"
    "callbackFetchKey"

    "returnUrl",
    "returnBody",

    "endUser",
    "saveKey",
    "insertOnly",

    "detectMime",
    "mimeLimit",
    "fsizeLimit",

    "persistentOps",
    "persistentNotifyUrl",
    "persistentPipeline",
])

_deprecated_policy_fields = set([
    "asyncOps"
])
"""

AK = "OyPuCLYfJExWEB0V0_lTXA4i7Ic2SI8I2NOwq7Jf"
SK = "zFae7U03gwm4PBFSHb1dvwT6cQMXL3VQ2-k6CIdN"
BUCKET = "hfut-uploads"

q = Auth(AK, SK)

# 直接上传二进制流

key = "测试"
data = "什么鬼"
token = q.upload_token(BUCKET)
ret, info = put_data(token, key, data, mime_type="application/octet-stream", check_crc=True)
print info.status_code
print ret


# 上传本地文件

localfile = __file__
key = "test_file"
mime_type = "text/plain"
params = {"x:a": "a"}

token = q.upload_token(BUCKET, key)
ret, info = put_file(token, key, localfile, mime_type=mime_type, check_crc=True)
print(info)

assert ret["hash"] == etag(localfile)

"""
# 断点续上传、分块并行上传
mime_type = "text/plain"
params = {"x:a": "a"}
localfile = ".../.../..."

key = "big"
token = q.upload_token(bucket_name, key)

progress_handler = lambda progress, total: progress
ret, info = put_file(token, key, localfile, params, mime_type, progress_handler=progress_handler)
print(info)
assert ret["key"] == key

# 下载私有文件
bucket = "test_private_bucket"
key = "test_private_key"
base_url = "http://%s/%s" % (bucket + ".qiniudn.com", key)
private_url = q.private_download_url(base_url, expires=3600)
print(private_url)
r = requests.get(private_url)
assert r.status_code == 200

# 资源操作
bucket = BucketManager(q)

# 获取文件信息
key = "..."
ret, info = bucket.stat(bucket_name, key)
print(info)
assert "hash" in ret

# 复制文件
key = "..."
ret, info = bucket.copy(bucket_name, "copyfrom", bucket_name, key)
print(info)
assert ret == {}

# 移动文件
key = "..."
key2 = key + "move"
ret, info = bucket.move(bucket_name, key, bucket_name, key2)
print(info)
assert ret == {}

# 删除文件
key = "..."
ret, info = bucket.delete(bucket_name, key)
print(info)
assert ret is None
assert info.status_code == 612

# 抓取资源
ret, info = bucket.fetch("http://developer.qiniu.com/docs/v6/sdk/python-sdk.html", bucket_name, "fetch.html")
print(info)
assert ret == {}

# 更新镜像资源
ret, info = bucket.prefetch(bucket_name, "python-sdk.html")
print(info)
assert ret == {}

# 批量操作
# 批量获取文件信息
from qiniu import build_batch_stat

ops = build_batch_stat(bucket_name, ["python-sdk.html","python-sdk2.html"])
ret, info = bucket.batch(ops)
print(info)
assert ret[0]["code"] == 200

# 批量复制文件
from qiniu import build_batch_copy

key = "copyto"
ops = build_batch_copy(bucket_name, {"copyfrom": key}, bucket_name)
ret, info = bucket.batch(ops)
print(info)
assert ret[0]["code"] == 200

# 批量移动文件
from qiniu import build_batch_move

key = "moveto"
key2 = key + "move"
ops = build_batch_move(bucket_name, {key: key2}, bucket_name)
ret, info = bucket.batch(ops)
print(info)
assert ret[0]["code"] == 200

# 批量删除文件
from qiniu import build_batch_delete

ops = build_batch_delete(bucket_name, ["python-sdk.html"])
ret, info = bucket.batch(ops)
print(info)
assert ret[0]["code"] == 612

# 高级管理操作
ret, eof, info = bucket.list(bucket_name, limit=4)
print(info)
assert eof is False
assert len(ret.get("items")) == 4

ret, eof, info = bucket.list(bucket_name, limit=100)
print(info)
assert eof is True

# 从上一次list_prefix的位置继续列出文件
ret2, eof, info = bucket.list(bucket_name, prefix="test", marker=ret["marker"], limit=1)
print(info)
assert eof is True
一个典型的对整个bucket遍历的操作为：

q = Auth(access_key, secret_key)

def list_all(bucket_name, bucket=None, prefix=None, limit=None):
    if bucket is None:
        bucket = BucketManager(q)
    marker = None
    eof = False
    while eof is False:
        ret, eof, info = bucket.list(bucket_name, prefix=prefix, marker=marker, limit=limit)
        marker = ret.get("marker", None)
        for item in ret["items"]:
            print(item["key"])
            pass
    if eof is not True:
        # 错误处理
        pass


# 云处理
持久化处理

# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, PersistentFop, build_op, op_save

access_key = "..."
secret_key = "..."
bucket_src = "..."
key_src = "..."
saved_bucket = "..."
saved_key = "..."
pipeline = "..."

q = Auth(access_key, secret_key)

pfop = PersistentFop(q, bucket_src, pipeline)
op = op_save("avthumb/m3u8/segtime/10/vcodec/libx264/s/320x240", saved_bucket, saved_key)
ops = []
ops.append(op)
ret, info = pfop.execute(key_src, ops, 1)
print(info)
assert ret["persistentId"] is not None

"""