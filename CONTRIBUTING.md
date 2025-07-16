# Contributing to langchain-iointelligence

Thank you for your interest in contributing to langchain-iointelligence! 🎉

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/langchain-iointelligence.git
   cd langchain-iointelligence
   ```

3. **Set up development environment**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

## 🧪 Testing

Before submitting changes, please run the tests:

```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=langchain_iointelligence

# Run specific test file
pytest tests/test_llm.py -v
```

## 📝 Code Style

We use several tools to maintain code quality:

```bash
# Format code
black langchain_iointelligence/ tests/

# Type checking
mypy langchain_iointelligence/

# Linting
flake8 langchain_iointelligence/ tests/
```

## 🐛 Bug Reports

When filing bug reports, please include:
- Python version
- LangChain version
- langchain-iointelligence version
- Minimal reproduction code
- Expected vs actual behavior

## 💡 Feature Requests

For feature requests, please:
- Explain the use case
- Provide examples of how it would be used
- Consider backward compatibility

## 📄 Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update examples if API changes

## 🔄 Pull Request Process

1. **Update version** in `setup.py` if appropriate
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Ensure tests pass**
5. **Create pull request** with clear description

## 📧 Questions?

Feel free to open an issue for any questions or discussions!

## 🎯 Development Priorities

Current focus areas:
- [ ] LangChain ChatModel support
- [ ] Streaming output support
- [ ] Async/await support
- [ ] More comprehensive error handling
- [ ] Performance optimizations

Thank you for contributing! 🙏
