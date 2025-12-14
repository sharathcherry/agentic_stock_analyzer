# 🚀 Quick Reference: NVIDIA API Setup

## 1️⃣ Get Your API Key (2 minutes)

Visit: **https://build.nvidia.com/explore/discover**

1. Sign in with NVIDIA account (create free if needed)
2. Browse AI models
3. Click "Get API Key" on any model page
4. Copy the key (starts with `nvapi-`)

## 2️⃣ Add to Your `.env` File

Open: `backend/.env`

Replace `your_nvidia_api_key_here` with your actual key:

```env
NVIDIA_API_KEY=nvapi-YOUR_ACTUAL_KEY_HERE
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-405b-instruct
```

## 3️⃣ Restart Backend (if needed)

If the server isn't auto-reloading:

```bash
cd backend
# Press Ctrl+C to stop current server
uvicorn app.main:app --reload
```

## 4️⃣ Test It!

```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"healthy","services":{"api":"online"}}
```

## 📝 Model Options

Change `NVIDIA_MODEL` in `.env` to:

| Model | Value | When to Use |
|-------|-------|-------------|
| **Llama 3.1 405B** (Recommended) | `meta/llama-3.1-405b-instruct` | Best quality, complex analysis |
| **Llama 3.1 70B** (Fast) | `meta/llama-3.1-70b-instruct` | Good balance of speed & quality |
| **Mistral 8x7B** (Faster) | `mistralai/mixtral-8x7b-instruct-v0.1` | Quick responses |
| **Llama 3.1 8B** (Fastest) | `meta/llama-3.1-8b-instruct` | Simple tasks, low latency |

## ✅ Verification Checklist

- [ ] Created NVIDIA account
- [ ] Got API key (starts with `nvapi-`)
- [ ] Pasted key into `backend/.env`
- [ ] Backend server running
- [ ] Health check returns OK

## 🆘 Troubleshooting

**Problem**: "Invalid API key"  
**Solution**: Copy the key again, check for spaces

**Problem**: "Rate limit exceeded"  
**Solution**: Wait 24h or upgrade to paid tier

**Problem**: Server not connecting  
**Solution**: Check `NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1`

## 📚 Full Documentation

- **Complete Guide**: `NVIDIA_API_GUIDE.md`
- **Migration Details**: `MIGRATION_SUMMARY.md`
- **Setup Guide**: `SETUP_GUIDE.md`

---

**That's it! You're ready to use NVIDIA-powered AI for stock analysis! 🎉**
