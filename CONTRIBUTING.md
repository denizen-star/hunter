# Contributing to Job Hunter

Thank you for your interest in contributing to Job Hunter! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, constructive, and collaborative.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Ollama version)
   - Error messages and logs

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Why this would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/hunter.git
cd hunter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

## Testing

```bash
# Run tests (when implemented)
pytest

# Check code style
black app/
flake8 app/
```

## Documentation

- Update docs/ if adding features
- Update README.md if changing setup/usage
- Update CHANGELOG.md for all changes
- Add docstrings to new functions/classes

## Commit Messages

Use clear, descriptive commit messages:

```
Add feature: Brief description

- Detailed point 1
- Detailed point 2
```

## Areas for Contribution

- **Bug fixes**: Fix reported issues
- **Documentation**: Improve docs, add examples
- **Tests**: Add unit and integration tests
- **Features**: Implement requested features
- **UI/UX**: Improve web interface
- **Performance**: Optimize AI processing
- **Integrations**: Add new AI providers, export formats

## Questions?

Open an issue for questions or discussions.

---

Thank you for contributing! 🎯

