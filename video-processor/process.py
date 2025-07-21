import os
import boto3
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

# R2 Credentials
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")


s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
)

def process_video(key: str):
    """
    Downloads a video from R2, compresses it with ffmpeg, and uploads the result back to R2.
    """
    input_path = f"/tmp/{key.split('/')[-1]}"
    output_path = f"/tmp/compressed-{key.split('/')[-1]}"

    print(f"Downloading {key} to {input_path}...")
    s3.download_file(R2_BUCKET_NAME, key, input_path)

    print(f"Compressing {input_path} to {output_path}...")
    ffmpeg_command = [
        "ffmpeg",
        "-i", input_path,
        "-preset", "faster",
        "-c:v", "libx265",
        "-s", "854x480",
        "-x265-params", "bframes=8:psy-rd=1:ref=3:aq-mode=3:aq-strength=0.8:deblock=1,1",
        "-metadata", "title=Encoded By mohammadham",
        "-pix_fmt", "yuv420p",
        "-crf", "30",
        "-c:a", "libopus",
        "-b:a", "32k",
        "-c:s", "copy",
        "-map", "0",
        "-ac", "2",
        "-ab", "32k",
        "-vbr", "2",
        "-level", "3.1",
        "-threads", "1",
        output_path,
    ]
    subprocess.run(ffmpeg_command, check=True)

    output_key = f"compressed/{key}"
    print(f"Uploading {output_path} to R2 at {output_key}...")
    s3.upload_file(output_path, R2_BUCKET_NAME, output_key)

    print("Cleaning up local files...")
    os.remove(input_path)
    os.remove(output_path)

    print("Notifying worker...")
    telegram_api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    chat_id = key.split('/')[0]
    text = f"/done {key}"
    requests.post(telegram_api_url, json={"chat_id": chat_id, "text": text})


    print("Done.")

if __name__ == "__main__":
    # This is an example of how to use the function.
    # In a real application, this would be triggered by a message from the Cloudflare Worker.
    # For example, you could use a message queue like SQS or a simple HTTP request.
    if len(os.sys.argv) > 1:
        process_video(os.sys.argv[1])
    else:
        print("Please provide the key of the video to process.")
        print("Usage: python process.py <key>")
