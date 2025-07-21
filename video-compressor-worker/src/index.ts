import { Telegraf } from 'telegraf';
import { sign } from 'aws4';

export interface Env {
  BOT_TOKEN: string;
  VIDEO_BUCKET: R2Bucket;
  R2_ACCESS_KEY_ID: string;
  R2_SECRET_ACCESS_KEY: string;
  R2_ACCOUNT_ID: string;
  PROCESSOR_URL: string;
}

async function getPresignedUrl(env: Env, key: string): Promise<string> {
  const url = new URL(`https://<${env.R2_ACCOUNT_ID}>.r2.cloudflarestorage.com/${env.VIDEO_BUCKET.id}/${key}`);

  const request = {
    host: url.host,
    path: url.pathname,
    method: 'PUT',
    headers: {
      'Content-Type': 'application/octet-stream',
    },
    service: 's3',
    region: 'auto',
  };

  const signedRequest = sign(request, {
    accessKeyId: env.R2_ACCESS_KEY_ID,
    secretAccessKey: env.R2_SECRET_ACCESS_KEY,
  });

  return `https://${signedRequest.host}${signedRequest.path}`;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const bot = new Telegraf(env.BOT_TOKEN);

    bot.start((ctx) => ctx.reply('Welcome! Send me a video to compress.'));

    bot.on('video', async (ctx) => {
      const video = ctx.message.video;
      const key = `${ctx.from.id}/${video.file_unique_id}.mp4`;

      try {
        const presignedUrl = await getPresignedUrl(env, key);

        // Trigger the processor service
        await fetch(env.PROCESSOR_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ key }),
        });

        await ctx.reply(`Please upload your video to this URL: ${presignedUrl}`);
      } catch (error) {
        console.error(error);
        await ctx.reply('Sorry, something went wrong while preparing the upload.');
      }
    });

    // This endpoint will be called by the processor service when it's done.
    bot.command('done', async (ctx) => {
        const key = ctx.message.text.split(' ')[1];
        if (!key) {
            return ctx.reply('Invalid completion notification.');
        }

        const compressedKey = `compressed/${key}`;
        // For simplicity, we're just sending a message.
        // In a real app, you'd generate a presigned GET URL for the user to download the file.
        await ctx.telegram.sendMessage(key.split('/')[0], `Your video has been compressed! You can find it at ${compressedKey}`);
    });


    try {
      const payload = await request.json();
      await bot.handleUpdate(payload);
      return new Response('OK');
    } catch (error) {
      console.error(error);
      return new Response('Error handling update', { status: 500 });
    }
  },
};
