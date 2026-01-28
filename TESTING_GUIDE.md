# Testing Strategy - Personal Development App

## 🎯 Testing Philosophy

**Test-Driven Development (TDD) - MANDATORY**

Every feature must have tests. No code gets merged without tests.

---

## 📋 Testing Requirements

### Coverage Requirements
- **Minimum:** 80% code coverage for all new code
- **Target:** 90%+ coverage for critical paths (auth, data integrity)
- **100% coverage:** Models, serializers, critical business logic

### Testing Pyramid
```
           E2E Tests (10%)
          Integration Tests (20%)
         Unit Tests (70%)
```

---

## 🧪 Test Structure

### Directory Organization
```
backend/
├── core/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py         # User model tests
│       ├── test_views.py          # API endpoint tests
│       ├── test_serializers.py    # Validation tests
│       └── test_permissions.py    # Auth & permission tests
│
├── habits/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py         # Habit, HabitLog model tests
│       ├── test_views.py          # CRUD endpoint tests
│       ├── test_serializers.py    # Habit serializer tests
│       ├── test_services.py       # Business logic tests
│       └── test_permissions.py    # Permission tests
│
└── pytest.ini                      # Pytest configuration
```

---

## 🔧 Pytest Configuration

### Create pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

---

## ✍️ Writing Tests

### 1. Model Tests (test_models.py)

```python
import pytest
from django.contrib.auth import get_user_model
from core.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    """Test User model and profile."""
    
    def test_create_user(self):
        """Test creating a user with profile."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert hasattr(user, 'profile')
    
    def test_user_profile_auto_created(self):
        """Test that profile is created automatically."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert UserProfile.objects.filter(user=user).exists()
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(username='testuser')
        assert str(user) == 'testuser'
```

### 2. View Tests (test_views.py)

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""
    
    def setup_method(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_user_signup(self):
        """Test user registration."""
        response = self.client.post('/api/auth/signup/', self.user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert User.objects.filter(username='testuser').exists()
    
    def test_user_login(self):
        """Test user login with JWT."""
        # Create user first
        User.objects.create_user(**self.user_data)
        
        # Login
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password."""
        User.objects.create_user(**self.user_data)
        
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### 3. Serializer Tests (test_serializers.py)

```python
import pytest
from core.serializers import UserSerializer, UserProfileSerializer

@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer validation."""
    
    def test_valid_user_data(self):
        """Test serializer with valid data."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        assert serializer.is_valid()
    
    def test_invalid_email(self):
        """Test serializer rejects invalid email."""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_password_min_length(self):
        """Test password minimum length validation."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'  # Too short
        }
        serializer = UserSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
```

### 4. Service Tests (test_services.py)

```python
import pytest
from habits.services import HabitSuggestionService
from habits.models import Habit

@pytest.mark.django_db
class TestHabitSuggestionService:
    """Test habit suggestion algorithm."""
    
    def setup_method(self):
        """Create test user and habits."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser')
        
        # Create existing habits
        self.morning_habit = Habit.objects.create(
            user=self.user,
            name='Morning run',
            time='07:00',
            location='Park'
        )
    
    def test_get_time_based_suggestions(self):
        """Test suggestions based on time."""
        service = HabitSuggestionService(self.user)
        suggestions = service.get_habits_by_time('07:00')
        
        assert len(suggestions) > 0
        assert 'Morning' in suggestions[0]['name']
    
    def test_suggestion_algorithm_accuracy(self):
        """Test suggestion algorithm returns relevant habits."""
        service = HabitSuggestionService(self.user)
        suggestions = service.suggest_stacking_opportunities()
        
        assert len(suggestions) <= 3  # Max 3 suggestions
        for suggestion in suggestions:
            assert 'anchor_habit' in suggestion
            assert 'suggested_habit' in suggestion
```

---

## 🚀 Running Tests

### Basic Commands

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run all tests
pytest backend/

# Run with verbose output
pytest backend/ --verbose

# Run specific test file
pytest backend/core/tests/test_models.py

# Run specific test class
pytest backend/core/tests/test_models.py::TestUserModel

# Run specific test function
pytest backend/core/tests/test_models.py::TestUserModel::test_create_user

# Run tests with coverage
pytest backend/ --cov=backend --cov-report=html

# Run only unit tests
pytest backend/ -m unit

# Run tests and stop on first failure
pytest backend/ -x

# Run tests in parallel (faster)
pytest backend/ -n auto
```

### Coverage Reports

```bash
# Generate HTML coverage report
pytest backend/ --cov=backend --cov-report=html

# Open coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux

# Terminal coverage report
pytest backend/ --cov=backend --cov-report=term-missing

# Check coverage threshold (fail if below 80%)
pytest backend/ --cov=backend --cov-fail-under=80
```

---

## 📝 Testing Checklist (Before Every Commit)

```bash
# 1. Format code
black backend/
isort backend/

# 2. Lint code
flake8 backend/

# 3. Run all tests
pytest backend/ --verbose

# 4. Check coverage
pytest backend/ --cov=backend --cov-report=term-missing

# 5. Verify coverage threshold
pytest backend/ --cov=backend --cov-fail-under=80

# 6. If all pass, commit
git add .
git commit -m "feat(module): description with tests"
git push
```

---

## 🎯 Testing Best Practices

### 1. Test First (TDD)
```python
# 1. Write the test (it will fail)
def test_habit_streak_calculation():
    habit = Habit.objects.create(name="Test")
    assert habit.calculate_streak() == 0

# 2. Implement the feature
def calculate_streak(self):
    return 0  # Minimal implementation

# 3. Run test (should pass)
# 4. Refactor if needed
```

### 2. One Assertion Per Test
```python
# ❌ Bad: Multiple assertions
def test_user_creation():
    user = create_user()
    assert user.username == 'test'
    assert user.email == 'test@example.com'
    assert user.is_active == True

# ✅ Good: Separate tests
def test_user_username():
    user = create_user()
    assert user.username == 'test'

def test_user_email():
    user = create_user()
    assert user.email == 'test@example.com'

def test_user_is_active_by_default():
    user = create_user()
    assert user.is_active == True
```

### 3. Use Fixtures for Setup
```python
@pytest.fixture
def authenticated_user(db):
    """Create and return authenticated user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        password='testpass123'
    )

def test_habit_creation(authenticated_user):
    """Test habit creation with fixture."""
    habit = Habit.objects.create(
        user=authenticated_user,
        name='Test habit'
    )
    assert habit.user == authenticated_user
```

### 4. Test Edge Cases
```python
def test_habit_streak_with_no_logs():
    """Test streak when no logs exist."""
    habit = Habit.objects.create(name="Test")
    assert habit.calculate_streak() == 0

def test_habit_streak_with_gap():
    """Test streak resets after gap."""
    habit = Habit.objects.create(name="Test")
    # Create logs with gap
    create_log(habit, date='2026-01-01')
    create_log(habit, date='2026-01-03')  # Gap on 01-02
    assert habit.calculate_streak() == 1  # Only counts recent streak
```

### 5. Mock External Services
```python
from unittest.mock import patch

@patch('habits.services.send_notification')
def test_habit_reminder_sent(mock_send):
    """Test notification is sent."""
    habit = Habit.objects.create(name="Test")
    habit.send_reminder()
    
    mock_send.assert_called_once()
```

---

## 🐛 Debugging Failed Tests

```bash
# Run with extra verbosity
pytest backend/ -vv

# Show local variables on failure
pytest backend/ -l

# Enter debugger on failure
pytest backend/ --pdb

# Show print statements
pytest backend/ -s

# Run last failed tests only
pytest backend/ --lf

# Run tests that failed first
pytest backend/ --ff
```

---

## 📊 CI/CD Integration (Week 1)

### GitHub Actions Workflow
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.14
      - run: pip install -r requirements-day1.txt
      - run: pytest backend/ --cov=backend --cov-fail-under=80
```

---

**Remember: Tests are not optional. They are your safety net.**

Write tests. Run tests. Ship with confidence. 🚀
