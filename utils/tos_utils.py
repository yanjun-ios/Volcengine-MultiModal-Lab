import os
import tos
from tos import GranteeType, CannedType, PermissionType
from tos.models2 import Grantee, Grant, Owner

def upload_to_tos(object_key="", content="", bucket_name=None):
    """上传文件到TOS云存储"""
    ak = os.environ.get("VOLC_ACCESSKEY", "")
    sk = os.environ.get("VOLC_SECRETKEY", "")
    region = os.environ.get("REGION", "cn-beijing")
    bucket_name = os.environ.get("TOS_BUCKET_NAME", "default-bucket")
    endpoint = f"tos-{region}.volces.com"
    try:
        client = tos.TosClientV2(ak, sk, endpoint, region)
        # 上传
        result = client.put_object(bucket_name, object_key, content=content)
        client.put_object_acl(bucket_name, object_key, acl=tos.ACLType.ACL_Public_Read)
        
        url = f"https://{bucket_name}.{endpoint}/{object_key}"
        print(f"Successfully uploaded to TOS {url}")
        return url
    except Exception as e:
        print('upload file to tos fail with error: {}'.format(e))
        return None