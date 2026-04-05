Check usage, credits, and costs across all subscriptions including Anthropic, ElevenLabs, AWS, OpenAI, Supabase, Gemini, and Apify.

Execute:
```bash
cd .claude/skills/subscription-usage-checker/scripts && python check_all.py
```

After checking all services, provide a summary including:
- Services with high usage (>50% of quota)
- Any services with errors
- Total estimated monthly costs
- Recommendations for cost optimization

For individual service checks:
- **Anthropic**: `python check_anthropic.py`
- **ElevenLabs**: `python check_elevenlabs.py`
- **AWS**: `python check_aws.py --by-service`
- **OpenAI**: `python check_openai.py`
- **Supabase**: `python check_supabase.py`
- **Gemini**: `python check_gemini.py`
- **Apify**: `python check_apify.py`
