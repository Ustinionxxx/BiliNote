import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_OFFLINE'] = '0'

from huggingface_hub import snapshot_download

model_dir = '/home/xingsijia/projects/BiliNote/backend/models/whisper-cache'
os.makedirs(model_dir, exist_ok=True)

print('⬇️  开始下载模型（约150MB，需要几分钟）...')
snapshot_download(repo_id='Systran/faster-whisper-base', cache_dir=model_dir)
print('✅ 模型下载完成！')
