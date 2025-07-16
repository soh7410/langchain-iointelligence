# langchain-iointelligence

[![PyPI version](https://badge.fury.io/py/langchain-iointelligence.svg)](https://badge.fury.io/py/langchain-iointelligence)
[![Python versions](https://img.shields.io/pypi/pyversions/langchain-iointelligence.svg)](https://pypi.org/project/langchain-iointelligence/)
[![License](https://img.shields.io/pypi/l/langchain-iointelligence.svg)](https://pypi.org/project/langchain-iointelligence/)
[![Downloads](https://pepy.tech/badge/langchain-iointelligence)](https://pepy.tech/project/langchain-iointelligence)

> **📦 [Available on PyPI](https://pypi.org/project/langchain-iointelligence/)** - Install with `pip install langchain-iointelligence`

A lightweight wrapper for using io Intelligence LLM API with LangChain. Provides `IOIntelligenceLLM` that inherits from `BaseLLM` and integrates seamlessly with LangChain chains and agents.

## 🚀 Features

* Compatible with LangChain standard components like `LLMChain`, `Agent`, `PromptTemplate`
* Environment variable management via `.env` files (easy dev/prod switching)
* OpenAI-compatible API format support (`prompt`, `model`, `max_tokens`, etc.)

## 🧱 Directory Structure

```
langchain-iointelligence/
├── langchain_iointelligence/
│   ├── __init__.py
│   └── llm.py                    # IOIntelligenceLLM implementation
├── .env.example                  # IO_API_KEY, IO_API_URL template
├── setup.py
├── pyproject.toml
├── README.md
└── tests/
    └── test_llm.py              # Test code for functionality verification
```

## ⚙️ Installation

```bash
pip install langchain-iointelligence
```

Or for local development:

```bash
pip install -e .
```

## 🔐 Environment Variables Setup (`.env`)

```env
IO_API_KEY=your_api_key_here
IO_API_URL=https://api.intelligence.io.solutions/api/v1/chat/completions
```

## 🧪 Usage Examples (Direct Call)

```python
from langchain_iointelligence.llm import IOIntelligenceLLM

# Direct API configuration
llm = IOIntelligenceLLM(
    api_key="your_api_key_here",
    api_url="https://api.intelligence.io.solutions/api/v1/chat/completions"
)

# Or use environment variables (if configured in .env file)
llm = IOIntelligenceLLM()

# Modern usage (recommended)
response = llm.invoke("Tell me a fun fact about koalas.")
print(response)

# Legacy usage (deprecated but functional)
response = llm("Tell me a fun fact about koalas.")
print(response)
```

## 🔄 LangChain Chain Usage Examples

### Modern Approach (Recommended)

```python
from langchain_core.prompts import PromptTemplate
from langchain_iointelligence.llm import IOIntelligenceLLM

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")
llm = IOIntelligenceLLM()

# Modern approach: prompt | llm
chain = prompt_template | llm
result = chain.invoke({"topic": "robots"})
print(result)
```

### Legacy Approach (Deprecated but Functional)

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_iointelligence.llm import IOIntelligenceLLM

prompt = PromptTemplate.from_template("Tell me a joke about {topic}")
llm = IOIntelligenceLLM()
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("robots"))
```

## 🛠️ Customization Examples

```python
from langchain_iointelligence.llm import IOIntelligenceLLM

# Customize parameters
llm = IOIntelligenceLLM(
    model="meta-llama/Llama-3.3-70B-Instruct",  # Main model
    max_tokens=500,
    temperature=0.3
)

# Other available models (see io Intelligence documentation for details)
# - meta-llama/Llama-3.3-70B-Instruct
# - Check API documentation for other models

response = llm.invoke("Explain quantum computing in simple terms.")
print(response)
```

## 🧼 API Response Format

io Intelligence API requires `OpenAI`-compatible JSON structure:

```json
{
  "choices": [
    {
      "message": {
        "content": "Generated text here"
      }
    }
  ]
}
```

If different, adjust `response.json()["choices"][0]["message"]["content"]` in `llm.py`.

## ✅ Supported Environment

* Python 3.8+
* LangChain 0.1+
* Valid io Intelligence API key

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=langchain_iointelligence
```

## 🔧 Development Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/langchain-iointelligence.git
cd langchain-iointelligence

# Install development packages
pip install -e ".[dev]"

# Set environment variables
cp .env.example .env
# Edit .env file to set API keys

# Code formatting
black langchain_iointelligence/ tests/

# Type checking
mypy langchain_iointelligence/

# Linting
flake8 langchain_iointelligence/ tests/
```

## 📚 Future Extensions (Optional)

* LangChain `ChatModel` support
* Streaming output support
* Multiple model switching support
* Asynchronous processing support
* More detailed error handling

## 📄 License

MIT License

## 🤝 Contributing

Pull requests and issues are welcome!

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📧 Support

For questions or support, please create an issue at [Issues](https://github.com/yourusername/langchain-iointelligence/issues).
