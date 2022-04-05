from qiniu import Auth, put_data

access_key = 'qrzSyJQhCKCkThnsb2hAe7dl1TQP3vqD3yoxcmpp'
secret_key = 'No16ycda_F-MsKNglJNJSKYtjJWc8h1L92XYJTlJ'
# 七牛云创建的储存空间名称
bucket_name = 'junsircoding'

# 构建鉴权对象
q = Auth(access_key, secret_key)


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print('ret=====', ret)
        print('info====', info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception('上传图片失败')
    return ret['key']


if __name__ == '__main__':
    file = input('请输入路径')
    with open(file, 'rb') as f:
        storage(f.read())