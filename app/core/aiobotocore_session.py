from aiobotocore.session import AioSession


def get_aws_session() -> AioSession:
    """
    Return a new session object.
    """
    return AioSession()
