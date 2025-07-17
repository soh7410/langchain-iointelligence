# langchain-iointelligence

[![PyPI version](https://badge.fury.io/py/langchain-iointelligence.svg)](https://badge.fury.io/py/langchain-iointelligence)
[![Python versions](https://img.shields.io/pypi/pyversions/langchain-iointelligence.svg)](https://pypi.org/project/langchain-iointelligence/)
[![License](https://img.shields.io/pypi/l/langchain-iointelligence.svg)](https://pypi.org/project/langchain-iointelligence/)
[![Downloads](https://pepy.tech/badge/langchain-iointelligence)](https://pepy.tech/project/langchain-iointelligence)

> **📦 [Available on PyPI](https://pypi.org/project/langchain-iointelligence/)** - Install with `pip install langchain-iointelligence`

A modern LangChain wrapper for io Intelligence LLM API with both **Text LLM** and **Chat Model** support. Provides seamless integration with LangChain's ecosystem including chains, agents, and prompt templates.

## 🚀 Features

* **Dual Interface Support**: Both `IOIntelligenceLLM` (text-based) and `IOIntelligenceChatModel` (message-based)
* **Modern LangChain Compatibility**: Full support for `prompt | llm | parser` chains and `AIMessage` responses
* **OpenAI-Compatible API**: Supports both Chat (`messages`) and Completion (`prompt`) API formats
* **Runtime Configuration**: Easy provider switching with `configurable_alternatives()`
* **Fallback Support**: Robust error handling with `.with_fallbacks()` for production use
* **Environment Variable Management**: Seamless dev/prod switching via `.env` files

## 🧱 Architecture

```
langchain-iointelligence/
├── langchain_iointelligence/
│   ├── __init__.py
│   ├── llm.py                    # IOIntelligenceLLM (BaseLLM)
│   └── chat.py                   # IOIntelligenceChatModel (BaseChatModel)
├── examples/                     # Usage examples
├── tests/                        # Test suites
└── README.md
```

## ⚙️ Installation

```bash
pip install langchain-iointelligence
```

For development:
```bash
git clone https://github.com/yourusername/langchain-iointelligence.git
cd langchain-iointelligence
pip install -e ".[dev]"
```

## 🔐 Environment Setup

Create a `.env` file:

```env
IO_API_KEY=your_api_key_here
IO_API_URL=https://api.intelligence.io.solutions/api/v1/chat/completions
```

## 🎯 Quick Start

### Modern Chat Model (Recommended)

```python
from langchain_iointelligence import IOIntelligenceChat
from langchain_core.messages import HumanMessage

# Initialize chat model
chat = IOIntelligenceChat(
    model="meta-llama/Llama-3.3-70B-Instruct",
    temperature=0.7,
    max_tokens=1000
)

# Direct usage
messages = [HumanMessage(content="Tell me about quantum computing")]
response = chat.invoke(messages)
print(response.content)  # AIMessage content
```

### Text LLM (Legacy Support)

```python
from langchain_iointelligence import IOIntelligenceLLM

llm = IOIntelligenceLLM()
response = llm.invoke("Tell me about quantum computing")
print(response)  # String response
```

## 🔗 LangChain Integration Examples

### Modern Chain with Chat Model

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_iointelligence import IOIntelligenceChat

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    ("human", "Tell me a {adjective} joke about {topic}")
])

# Initialize chat model
chat = IOIntelligenceChat()

# Modern chain: prompt | chat
chain = prompt | chat
result = chain.invoke({"adjective": "funny", "topic": "robots"})
print(result.content)
```

### Runtime Provider Switching

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_iointelligence import IOIntelligenceChat

# Configure multiple providers
chat_io = IOIntelligenceChat()
chat_openai = ChatOpenAI()
chat_anthropic = ChatAnthropic()

# Runtime switching
configurable_chat = chat_openai.configurable_alternatives(
    which="provider",
    default_key="openai",
    iointelligence=chat_io,
    anthropic=chat_anthropic,
)

# Use with config
response = configurable_chat.invoke(
    "Hello, world!",
    config={"configurable": {"provider": "iointelligence"}}
)
```

### Fallback Configuration

```python
from langchain_openai import ChatOpenAI
from langchain_iointelligence import IOIntelligenceChat

# Primary and fallback models
primary = IOIntelligenceChat()
fallback = ChatOpenAI()

# Chain with fallback
reliable_chat = primary.with_fallbacks([fallback])

# Automatically switches on failure
response = reliable_chat.invoke("Explain machine learning")
```

### Advanced Chain with Output Parser

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_iointelligence import IOIntelligenceChat

prompt = ChatPromptTemplate.from_messages([
    ("system", "Respond in exactly 50 words"),
    ("human", "{question}")
])

chat = IOIntelligenceChat(temperature=0.3)
parser = StrOutputParser()

# Complete chain
chain = prompt | chat | parser

result = chain.invoke({"question": "What is artificial intelligence?"})
print(result)  # Clean string output
```

## 🎛️ Configuration Options

### Chat Model Parameters

```python
from langchain_iointelligence import IOIntelligenceChat

chat = IOIntelligenceChat(
    # API Configuration
    api_key="your_key",                           # or use IO_API_KEY env var
    api_url="https://api.example.com/v1/chat",    # or use IO_API_URL env var
    
    # Model Parameters
    model="meta-llama/Llama-3.3-70B-Instruct",   # Model name
    temperature=0.7,                              # Creativity (0.0-2.0)
    max_tokens=2000,                              # Response length
    timeout=30,                                   # Request timeout
    max_retries=3,                                # Retry attempts
)
```

### Text LLM Parameters

```python
from langchain_iointelligence import IOIntelligenceLLM

llm = IOIntelligenceLLM(
    api_key="your_key",
    api_url="https://api.example.com/v1/chat",
    model="meta-llama/Llama-3.3-70B-Instruct",
    temperature=0.5,
    max_tokens=1500,
)
```

## 🔌 API Compatibility

This library supports both OpenAI-compatible API formats:

**Chat Completion Format (Default):**
```json
{
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "messages": [{"role": "user", "content": "Hello"}],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Text Completion Format (Legacy):**
```json
{
  "model": "meta-llama/Llama-3.3-70B-Instruct", 
  "prompt": "Hello",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

The library automatically detects and parses both response formats.

## ✅ Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=langchain_iointelligence

# Run specific test
pytest tests/test_llm.py::TestIOIntelligenceLLM::test_call_success
```

## 🛠️ Development Setup

```bash
# Clone and install
git clone https://github.com/yourusername/langchain-iointelligence.git
cd langchain-iointelligence
pip install -e ".[dev]"

# Setup environment
cp .env.example .env
# Edit .env with your API credentials

# Code quality
black langchain_iointelligence/ tests/  # Formatting
mypy langchain_iointelligence/          # Type checking
flake8 langchain_iointelligence/        # Linting
```

## 🚀 Production Patterns

### Error Handling

```python
from langchain_iointelligence import IOIntelligenceChat
from langchain_core.exceptions import OutputParserException

chat = IOIntelligenceChat()

try:
    response = chat.invoke("Hello")
    print(response.content)
except OutputParserException as e:
    print(f"API Error: {e}")
    # Handle gracefully
```

### Retry Strategy

```python
from langchain_iointelligence import IOIntelligenceChat

# Built-in retry configuration
chat = IOIntelligenceChat(
    max_retries=5,
    timeout=60
)
```

### Multi-Provider Setup

```python
# Production-ready multi-provider configuration
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic  
from langchain_iointelligence import IOIntelligenceChat

# Define provider chain with fallbacks
primary = IOIntelligenceChat(model="meta-llama/Llama-3.3-70B-Instruct")
secondary = ChatOpenAI(model="gpt-4")
tertiary = ChatAnthropic(model="claude-3-sonnet-20240229")

# Chain with multiple fallbacks
robust_chat = primary.with_fallbacks([secondary, tertiary])

# Use in production
response = robust_chat.invoke("Process this request")
```

## 📊 Available Models

Check the io Intelligence API documentation for the latest model list. Common models include:

- `meta-llama/Llama-3.3-70B-Instruct` (default)
- `meta-llama/Llama-3.1-405B-Instruct`
- `meta-llama/Llama-3.1-70B-Instruct`

## 🔍 Migration Guide

### From v0.1.0 to v0.1.1+

**Old (Text LLM only):**
```python
from langchain_iointelligence import IOIntelligenceLLM
llm = IOIntelligenceLLM()
response = llm("Hello")  # String
```

**New (Recommended Chat Model):**
```python
from langchain_iointelligence import IOIntelligenceChat
from langchain_core.messages import HumanMessage

chat = IOIntelligenceChat()
response = chat.invoke([HumanMessage(content="Hello")])  # AIMessage
print(response.content)
```

### From OpenAI

**OpenAI:**
```python
from langchain_openai import ChatOpenAI
chat = ChatOpenAI(model="gpt-4", temperature=0.7)
```

**io Intelligence:**
```python
from langchain_iointelligence import IOIntelligenceChat
chat = IOIntelligenceChat(model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.7)
```

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest tests/`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/langchain-iointelligence/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/langchain-iointelligence/wiki)
- **Examples**: See `examples/` directory
