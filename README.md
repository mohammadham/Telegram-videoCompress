# Telegram Video Compressor (Cloudflare Worker Edition)

This is a Cloudflare Worker that compresses videos sent to a Telegram bot.

**DEV:** [mohammadham](https://github.com/mohammadham)

## Architecture

This project uses a hybrid architecture to handle video processing, which is not natively supported in the Cloudflare Workers environment.

1.  **Cloudflare Worker (`video-compressor-worker`):**
    *   Acts as the main entry point for the Telegram bot.
    *   Handles all interactions with the Telegram API.
    *   Generates presigned URLs for direct uploads to Cloudflare R2.
    *   Triggers the video processing service.
    *   Notifies the user when the compressed video is ready.

2.  **Video Processing Service (`video-processor`):**
    *   A separate service (in this case, a Python script) that can run `ffmpeg`.
    *   Downloads the original video from R2.
    *   Compresses the video using `ffmpeg`.
    *   Uploads the compressed video back to R2.
    *   Notifies the Cloudflare Worker when processing is complete.

3.  **Cloudflare R2:**
    *   Used for storing the original and compressed videos.

## Deployment

### 1. Cloudflare Worker

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/mohammadham/TG-videoCompress)

**Manual Deployment:**

1.  Clone this repository.
2.  Navigate to the `video-compressor-worker` directory.
3.  Install dependencies: `npm install`
4.  Set up your `wrangler.toml` file with your Cloudflare account details.
5.  Create a `.dev.vars` file and add the following secrets:
    *   `BOT_TOKEN`: Your Telegram bot token.
    *   `R2_ACCESS_KEY_ID`: Your R2 access key ID.
    *   `R2_SECRET_ACCESS_KEY`: Your R2 secret access key.
    *   `R2_ACCOUNT_ID`: Your Cloudflare account ID.
    *   `PROCESSOR_URL`: The URL of your video processing service.
6.  Deploy the worker: `npm run deploy`

### 2. Video Processing Service

1.  Navigate to the `video-processor` directory.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Create a `.env` file and add the following variables:
    *   `R2_ACCOUNT_ID`: Your Cloudflare account ID.
    *   `R2_ACCESS_KEY_ID`: Your R2 access key ID.
    *   `R2_SECRET_ACCESS_KEY`: Your R2 secret access key.
    *   `R2_BUCKET_NAME`: The name of your R2 bucket.
    *   `BOT_TOKEN`: Your Telegram bot token.
4.  Run the service. You will need a way to expose this service to the internet, for example, by running it on a VPS or as a serverless function on a platform like AWS Lambda or Google Cloud Functions.

## Original Python Project

The original Python project can be found in the `python-version` directory.
this project It's a port of the original [TG-videoCompress](https://github.com/Anshusharma75/TG-videoCompress) project, rewritten in TypeScript to run on the Cloudflare serverless platform.
