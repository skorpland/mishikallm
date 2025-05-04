import Image from '@theme/IdealImage';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Using MishikaLLM with OpenAI Codex

This guide walks you through connecting OpenAI Codex to MishikaLLM. Using MishikaLLM with Codex allows teams to:
- Access 100+ LLMs through the Codex interface
- Use powerful models like Gemini through a familiar interface
- Track spend and usage with MishikaLLM's built-in analytics
- Control model access with virtual keys

<Image img={require('../../img/mishikallm_codex.gif')} />

## Quickstart

:::info

Requires MishikaLLM v1.66.3.dev5 and higher

:::


Make sure to set up MishikaLLM with the [MishikaLLM Getting Started Guide](../proxy/docker_quick_start.md).

## 1. Install OpenAI Codex

Install the OpenAI Codex CLI tool globally using npm:

<Tabs>
<TabItem value="npm" label="npm">

```bash showLineNumbers
npm i -g @openai/codex
```

</TabItem>
<TabItem value="yarn" label="yarn">

```bash showLineNumbers
yarn global add @openai/codex
```

</TabItem>
</Tabs>

## 2. Start MishikaLLM Proxy

<Tabs>
<TabItem value="docker" label="Docker">

```bash showLineNumbers
docker run \
    -v $(pwd)/mishikallm_config.yaml:/app/config.yaml \
    -p 4000:4000 \
    ghcr.io/berriai/mishikallm:main-latest \
    --config /app/config.yaml
```

</TabItem>
<TabItem value="pip" label="MishikaLLM CLI">

```bash showLineNumbers
mishikallm --config /path/to/config.yaml
```

</TabItem>
</Tabs>

MishikaLLM should now be running on [http://localhost:4000](http://localhost:4000)

## 3. Configure MishikaLLM for Model Routing

Ensure your MishikaLLM Proxy is properly configured to route to your desired models. Create a `mishikallm_config.yaml` file with the following content:

```yaml showLineNumbers
model_list:
  - model_name: o3-mini
    mishikallm_params:
      model: openai/o3-mini
      api_key: os.environ/OPENAI_API_KEY
  - model_name: claude-3-7-sonnet-latest
    mishikallm_params:
      model: anthropic/claude-3-7-sonnet-latest
      api_key: os.environ/ANTHROPIC_API_KEY
  - model_name: gemini-2.0-flash
    mishikallm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY

mishikallm_settings:
  drop_params: true
```

This configuration enables routing to specific OpenAI, Anthropic, and Gemini models with explicit names.

## 4. Configure Codex to Use MishikaLLM Proxy

Set the required environment variables to point Codex to your MishikaLLM Proxy:

```bash
# Point to your MishikaLLM Proxy server
export OPENAI_BASE_URL=http://0.0.0.0:4000 

# Use your MishikaLLM API key (if you've set up authentication)
export OPENAI_API_KEY="sk-1234"
```

## 5. Run Codex with Gemini

With everything configured, you can now run Codex with Gemini:

```bash showLineNumbers
codex --model gemini-2.0-flash --full-auto
```

<Image img={require('../../img/mishikallm_codex.gif')} />

The `--full-auto` flag allows Codex to automatically generate code without additional prompting.

## 6. Advanced Options

### Using Different Models

You can use any model configured in your MishikaLLM proxy:

```bash
# Use Claude models
codex --model claude-3-7-sonnet-latest

# Use Google AI Studio Gemini models
codex --model gemini/gemini-2.0-flash
```

## Troubleshooting

- If you encounter connection issues, ensure your MishikaLLM Proxy is running and accessible at the specified URL
- Verify your MishikaLLM API key is valid if you're using authentication
- Check that your model routing configuration is correct
- For model-specific errors, ensure the model is properly configured in your MishikaLLM setup

## Additional Resources

- [MishikaLLM Docker Quick Start Guide](../proxy/docker_quick_start.md)
- [OpenAI Codex GitHub Repository](https://github.com/openai/codex)
- [MishikaLLM Virtual Keys and Authentication](../proxy/virtual_keys.md)
