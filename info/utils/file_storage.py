# _*_ coding:utf-8 _*_
# _*_ coding:utf-8 _*_

import qiniu

access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'


def upload_file(data):
    """上传文件到七牛云"""
    q = qiniu.Auth(access_key, secret_key)
    # key = 'hello'
    # data = 'hello qiniu!'
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)

    print(ret['key'])

    if info.status_code != 200:
        raise Exception('七牛上传失败')

    return ret['key']

    # if ret is not None:
    #     print('All is OK')
    # else:
    #     print(info)  # error message in info


# if __name__ == '__main__':
#     path = '/Users/zizle/Desktop/12.jpg'
#     with open(path, 'rb') as file:
#         upload_file(file.read())
