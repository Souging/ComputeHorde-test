import logging
import os
import re
import secrets
import uuid

import requests
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings
from django.core.management.base import BaseCommand
from requests import HTTPError

from compute_horde_validator.validator import s3

logger = logging.getLogger(__name__)
REGION_ERROR = re.compile(
    "the region '([a-z]+-[a-z]+-[0-9]+)' is wrong; expecting '([a-z]+-[a-z]+-[0-9]+)'"
)


def _print_region_env_warnings(writer):
    msg = ""
    if aws_region := os.getenv("AWS_REGION"):
        msg += f"You have environment variable AWS_REGION={aws_region}\n"
    if aws_default_region := os.getenv("AWS_DEFAULT_REGION"):
        msg += f"You have environment variable AWS_DEFAULT_REGION={aws_default_region}\n"

    if msg:
        msg = "Possible issues with environment variables:\n" + msg

    writer.write(msg)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--aws-access-key-id",
            help="Override the value of AWS_ACCESS_KEY_ID from .env",
        )
        parser.add_argument(
            "--aws-secret-access-key",
            help="Override the value of AWS_SECRET_ACCESS_KEY from .env",
        )
        parser.add_argument(
            "--aws-region-name",
            help="Override the value of AWS region (by default read from environment variable AWS_DEFAULT_REGION)",
        )
        parser.add_argument(
            "--aws-endpoint-url",
            help="Override the value of AWS_ENDPOINT_URL from .env",
        )
        parser.add_argument(
            "--s3-bucket-name-prompts",
            help="Override the value of S3_BUCKET_NAME_PROMPTS from .env",
        )
        parser.add_argument(
            "--s3-bucket-name-answers",
            help="Override the value of S3_BUCKET_NAME_ANSWERS from .env",
        )
        parser.add_argument(
            "--aws-signature-version",
            help="Override the value of AWS_SIGNATURE_VERSION from .env",
        )

    def handle(self, *args, **options):
        logging.basicConfig(level="ERROR")

        s3_client = s3.get_s3_client(
            aws_access_key_id=options["aws_access_key_id"],
            aws_secret_access_key=options["aws_secret_access_key"],
            region_name=options["aws_region_name"],
            endpoint_url=options["aws_endpoint_url"],
            signature_version=options["aws_signature_version"],
        )

        prompts_bucket = options["s3_bucket_name_prompts"] or settings.S3_BUCKET_NAME_PROMPTS
        answers_bucket = options["s3_bucket_name_answers"] or settings.S3_BUCKET_NAME_ANSWERS

        for bucket_name in (prompts_bucket, answers_bucket):
            test_file = f"diagnostic-{uuid.uuid4()}"
            file_contents = secrets.token_hex()

            # try generating a pre-signed url
            try:
                upload_url = s3.generate_upload_url(
                    test_file, bucket_name=bucket_name, s3_client=s3_client
                )
            except (NoCredentialsError, PartialCredentialsError):
                self.stderr.write(
                    "You did not provide credentials.\n"
                    "Please provide AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file.\n"
                    "For testing, you can also provide your credentials to this command with --aws-access-key-id and --aws-secret-access-key flags.\n",
                )
                return

            # try uploading to the pre-signed url
            try:
                s3.upload_prompts_to_s3_url(upload_url, file_contents)
            except HTTPError as exc:
                if exc.response.status_code == 403:
                    self.stderr.write(
                        f"Your configured credentials does not have permissions to write to this bucket: {bucket_name}\n"
                    )
                elif match := REGION_ERROR.search(exc.response.text):
                    wrong, expecting = match.groups()
                    self.stderr.write(
                        "Your bucket requests are being routed to a invalid AWS region.\n"
                    )
                    self.stderr.write(
                        f"Your bucket {bucket_name!r} is in region {expecting!r}, but it is configured as {wrong!r}\n"
                    )
                    _print_region_env_warnings(self.stderr)
                else:
                    self.stderr.write(
                        f"Failed to write to the bucket {bucket_name} with the following error:\n"
                        + str(exc)
                        + "\n"
                        + exc.response.text
                        + "Please check if the buckets you have configured exist and are accessible with the configured credentials.\n"
                    )
                return

            # try downloading with public url
            download_url = s3.get_public_url(
                test_file, bucket_name=bucket_name, s3_client=s3_client
            )
            response = requests.get(download_url)
            response.raise_for_status()  # TODO: handle status >= 400, but when would that happen?
            if response.status_code == 301:
                bucket_region = response.headers.get("x-amz-bucket-region")
                self.stderr.write(
                    "Your bucket requests are being routed to a invalid AWS region.\n"
                )
                if bucket_region:
                    self.stderr.write(
                        f"Your bucket {bucket_name!r} is in region {bucket_region!r}\n"
                    )
                _print_region_env_warnings(self.stderr)
                return

            assert file_contents == response.text.strip()
            self.stdout.write("\n\n🎉 Your S3 configuration works! 🎉")
