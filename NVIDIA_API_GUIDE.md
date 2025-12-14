# NVIDIA API Integration Guide

## Overview

This application now uses **NVIDIA's build.nvidia.com API** instead of OpenAI for LLM inference. NVIDIA provides access to state-of-the-art open-source models through an OpenAI-compatible API.

## Why NVIDIA API?

✅ **Free tier available** - Get started without costs  
✅ **Powerful models** - Access Meta Llama 3.1, Mistral, and other leading models  
✅ **OpenAI-compatible** - Drop-in replacement for OpenAI API  
✅ **Fast inference** - Optimized for NVIDIA GPUs  
✅ **No vendor lock-in** - Use open-source models  

## Getting Your NVIDIA API Key

1. **Visit** [https://build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover)
2. **Sign in** with your NVIDIA account (or create one - it's free!)
3. **Browse models** and select one (e.g., Meta Llama 3.1 405B Instruct)
4. **Generate API Key** - Click "Get API Key" button
5. **Copy your key** - It will start with `nvapi-`

## Available Models

### Recommended for Stock Analysis:

| Model | ID | Best For |
|-------|-----|----------|
| **Meta Llama 3.1 405B** | `meta/llama-3.1-405b-instruct` | Most powerful, best reasoning |
| **Meta Llama 3.1 70B** | `meta/llama-3.1-70b-instruct` | Balance of speed & quality |
| **Mistral 8x7B** | `mistralai/mixtral-8x7b-instruct-v0.1` | Fast, good for structured output |
| **Meta Llama 3.1 8B** | `meta/llama-3.1-8b-instruct` | Fastest, good for simple tasks |

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# NVIDIA API Configuration
NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.1-405b-instruct
```

### Changing Models

To switch models, simply update the `NVIDIA_MODEL` variable:

```env
# For faster responses (less cost)
NVIDIA_MODEL=meta/llama-3.1-70b-instruct

# For maximum accuracy
NVIDIA_MODEL=meta/llama-3.1-405b-instruct
```

## Code Changes Made

### 1. Updated `config.py`
```python
# NVIDIA API Configuration (build.nvidia.com)
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-405b-instruct")
```

### 2. Updated `ai_agent.py`
```python
self.llm = ChatOpenAI(
    model=settings.NVIDIA_MODEL,
    temperature=0.3,
    openai_api_key=settings.NVIDIA_API_KEY,
    openai_api_base=settings.NVIDIA_BASE_URL
)
```

## Testing the Integration

### 1. Start the backend:
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Test with curl:
```bash
curl -X POST http://localhost:8000/api/get_stock_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TATAMOTORS-EQ",
    "exchange": "NSE",
    "price_change_percent": -2.5
  }'
```

### 3. Check the response:
You should get AI-generated stock analysis with:
- Verdict (BUY/SELL/HOLD)
- Confidence score
- Detailed explanation
- Key factors
- Target price & stop loss

## Rate Limits & Pricing

### Free Tier
- **Requests**: Limited number per day
- **Models**: Access to all models
- **Speed**: Standard inference speed

### Paid Tier
- **Higher limits**: More requests per day
- **Faster**: Priority inference
- **Support**: Technical support included

Check [https://build.nvidia.com/pricing](https://build.nvidia.com/pricing) for current pricing.

## Troubleshooting

### Error: "Invalid API key"
- Verify your API key starts with `nvapi-`
- Check for extra spaces in `.env` file
- Regenerate key from NVIDIA dashboard

### Error: "Model not found"
- Verify model ID is correct
- Check available models at [https://build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover)

### Error: "Rate limit exceeded"
- You've hit the free tier limit
- Wait for limit reset (usually 24 hours)
- Consider upgrading to paid tier

### Slow responses
- Try a smaller model (70B or 8B instead of 405B)
- Check your internet connection
- NVIDIA servers might be under load

## Performance Comparison

| Model | Response Time | Quality | Cost |
|-------|--------------|---------|------|
| Llama 3.1 405B | ~3-5s | Excellent | Higher |
| Llama 3.1 70B | ~1-3s | Very Good | Medium |
| Mixtral 8x7B | ~1-2s | Good | Lower |
| Llama 3.1 8B | <1s | Good | Lowest |

## Migration from OpenAI

If you were using OpenAI previously:

1. ✅ **No code changes needed** - API is compatible
2. ✅ **Same response format** - JSON structure unchanged
3. ✅ **Better value** - Free tier + open models
4. ⚠️ **Different models** - Adjust prompts if needed

## Best Practices

### For Stock Analysis:
1. **Use Llama 3.1 70B or 405B** for complex analysis
2. **Set temperature to 0.3** for consistent predictions
3. **Include max_tokens** to control response length
4. **Handle rate limits** gracefully with retries

### Prompt Engineering:
- NVIDIA models respond well to **structured prompts**
- Request **JSON output** explicitly (as we do)
- Use **system messages** to set context
- Be **specific** about the analysis format

## Support & Resources

- **NVIDIA Documentation**: [https://docs.nvidia.com/ai-enterprise/](https://docs.nvidia.com/ai-enterprise/)
- **Model Cards**: [https://build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover)
- **API Reference**: [https://docs.api.nvidia.com/nim/reference/](https://docs.api.nvidia.com/nim/reference/)
- **Community**: [https://forums.developer.nvidia.com/](https://forums.developer.nvidia.com/)

## Next Steps

1. ✅ Get your NVIDIA API key
2. ✅ Update `.env` file
3. ✅ Test the integration
4. 🎯 Fine-tune model selection for your use case
5. 🎯 Monitor usage and performance
6. 🎯 Consider upgrading if you hit rate limits

---

**Happy Trading with NVIDIA-Powered AI! 🚀📈**
