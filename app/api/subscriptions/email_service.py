from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError
from fastapi import Depends
from pydantic import EmailStr
from app.core.aiobotocore_session import get_aws_session
from app.config import get_settings, Settings


async def get_ses_client(
    settings: Settings = Depends(get_settings), session: AioSession = Depends(get_aws_session)
) -> AioBaseClient:
    async with session.create_client(
        "ses",
        region_name=settings.AWS_SES_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    ) as client:
        yield client


class EmailService:
    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        ses_client=Depends(get_ses_client),
    ):
        self._ses_client = ses_client
        self._settings = settings

    async def send_email(self, to_email: EmailStr, subject: str, message: str) -> None:
        try:
            await self._ses_client.send_email(
                Source=self._settings.AWS_SES_VERIFIED_MAIL,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": message}},
                },
            )
        except ClientError as e:
            raise e
