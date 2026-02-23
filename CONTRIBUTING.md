# Contributing to OpenClaw Monitor

Thank you for your interest in contributing to OpenClaw Monitor! 🎉

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/yourusername/openclaw-monitor.git
cd openclaw-monitor
```

3. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. Run the development server:

```bash
export FLASK_ENV=development
export MONITOR_USERNAME=admin
export MONITOR_PASSWORD=dev
python3 app.py
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Code Quality

Before submitting a PR, ensure:

```bash
# Run linter
flake8 *.py

# Run type checker
mypy *.py

# Test functionality
python3 -m pytest tests/ -v
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semi colons, etc)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or correcting tests
- `chore:` - Changes to build process or auxiliary tools

Example:
```
feat(pricing): add support for custom exchange rates

- Add manual exchange rate input
- Add API endpoint for rate updates
- Store rate history in pricing.json
```

## Project Structure

```
openclaw-monitor/
├── app.py                 # Flask main application
├── pricing_manager.py     # Pricing configuration management
├── data_collector.py      # OpenClaw data collection
├── templates/
│   └── index.html        # Web interface
├── static/
│   ├── style.css         # Styles
│   └── dashboard.js      # Frontend logic
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── tests/                 # Test files
```

## Adding New Features

### Adding a New API Endpoint

1. Add the route in `app.py`
2. Add authentication decorator if needed
3. Add error handling
4. Update API documentation in README.md
5. Add tests

### Adding a New Model Pricing

1. Update `DEFAULT_PRICING` in `pricing_manager.py`
2. Add model information (provider, currency, etc.)
3. Test cost calculation

### Frontend Changes

1. Modify `templates/index.html` for structure
2. Modify `static/style.css` for styling
3. Modify `static/dashboard.js` for functionality
4. Ensure responsive design works on mobile

## Testing

### Manual Testing Checklist

- [ ] Fresh installation works
- [ ] Login with credentials works
- [ ] All tabs load correctly
- [ ] Pricing updates persist
- [ ] Cost calculations are correct
- [ ] Mobile layout works
- [ ] Dark/light theme switching works
- [ ] Auto-refresh works

### Test Data

Create a test OpenClaw environment:

```bash
mkdir -p ~/.openclaw/agents/main/sessions
echo '{"model": "test", "usage": {"total_tokens": 1000}}' > ~/.openclaw/agents/main/sessions/test.jsonl
```

## Submitting Changes

1. Create a new branch for your feature:

```bash
git checkout -b feature/my-new-feature
```

2. Make your changes and commit:

```bash
git add .
git commit -m "feat: add my new feature"
```

3. Push to your fork:

```bash
git push origin feature/my-new-feature
```

4. Open a Pull Request on GitHub

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass
- Request review from maintainers

## Reporting Issues

When reporting bugs, please include:

- Operating system and version
- Python version
- OpenClaw version
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

Feel free to open an issue for:
- Questions about the codebase
- Feature requests
- Bug reports
- Documentation improvements

Thank you for contributing! 🦞
