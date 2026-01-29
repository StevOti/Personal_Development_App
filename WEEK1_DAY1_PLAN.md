# Week 1 Day 1 Plan - Authentication System

## 🎯 Objective
Set up JWT authentication system with User model and API endpoints. Follow TDD approach - write tests first!

---

## 📋 Todo List (In Order)

### 1. Branch Setup (5 min)
```bash
git checkout -b feature/habits-mvp
git push -u origin feature/habits-mvp
```

### 2. Install Week 1 Packages (10 min)
```bash
.\venv\Scripts\Activate.ps1
cd backend
pip install djangorestframework-simplejwt==5.5.1
pip install django-cors-headers==4.3.1
pip install pytest-cov==4.1.0
pip freeze > ../requirements-frozen.txt
```

### 3. Configure Django Settings (15 min)
**File:** `backend/config/settings.py`
- Add `rest_framework`, `rest_framework_simplejwt`, `corsheaders` to INSTALLED_APPS
- Add JWT authentication configuration
- Add CORS settings for React (localhost:3000, localhost:5173)
- Configure REST_FRAMEWORK settings

### 4. Create User Model with Tests (TDD - 1 hour)
**Test First:** `backend/core/tests/test_models.py`
```python
# Write tests for:
- User creation
- User profile auto-creation
- Password hashing
- User string representation
```

**Then Implement:** `backend/core/models.py`
```python
# Create:
- UserProfile model (extends User)
- Fields: target_identity, onboarding_completed
- Signal to auto-create profile
```

**Run Tests:**
```bash
pytest backend/core/tests/test_models.py -v
```

### 5. Create User Serializers with Tests (TDD - 45 min)
**Test First:** `backend/core/tests/test_serializers.py`
```python
# Write tests for:
- User registration serializer validation
- Password min length validation
- Email format validation
- Profile serializer
```

**Then Implement:** `backend/core/serializers.py`
```python
# Create:
- UserSerializer (for registration)
- UserProfileSerializer
- LoginSerializer (optional)
```

**Run Tests:**
```bash
pytest backend/core/tests/test_serializers.py -v
```

### 6. Create Auth Endpoints with Tests (TDD - 1.5 hours)
**Test First:** `backend/core/tests/test_views.py`
```python
# Write tests for:
- POST /api/auth/signup/ (register new user)
- POST /api/auth/login/ (get JWT tokens)
- POST /api/auth/refresh/ (refresh access token)
- POST /api/auth/logout/ (blacklist refresh token)
- Invalid credentials handling
- Token validation
```

**Then Implement:** `backend/core/views.py`
```python
# Create views for:
- SignupView (APIView or CreateAPIView)
- LoginView (use TokenObtainPairView)
- TokenRefreshView (use TokenRefreshView)
- LogoutView
```

**Configure URLs:** `backend/core/urls.py`
```python
urlpatterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
]
```

**Include in main URLs:** `backend/config/urls.py`
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
```

**Run Tests:**
```bash
pytest backend/core/tests/test_views.py -v
```

### 7. Test Full Auth Flow Manually (30 min)
```bash
# Start server
python manage.py runserver

# Test with curl or Postman:
# 1. Register user: POST /api/auth/signup/
# 2. Login: POST /api/auth/login/
# 3. Use access token to access protected endpoint
# 4. Refresh token: POST /api/auth/refresh/
# 5. Logout: POST /api/auth/logout/
```

### 8. Run All Tests with Coverage (15 min)
```bash
# Uncomment coverage options in pytest.ini
pytest backend/ --cov=backend --cov-report=html --cov-report=term-missing

# Open coverage report
start htmlcov/index.html

# Ensure 80%+ coverage
```

### 9. Code Quality Check (15 min)
```bash
# Format code
black backend/
isort backend/

# Lint code
flake8 backend/

# Fix any issues
```

### 10. Commit Auth System (10 min)
```bash
git add .
git commit -m "feat(auth): implement JWT authentication with User model and API endpoints

- Add User model with UserProfile
- Add signup, login, refresh, logout endpoints
- Add comprehensive unit tests (80%+ coverage)
- Configure JWT and CORS settings"

git push origin feature/habits-mvp
```

---

## ⏰ Time Estimate
**Total: 4-5 hours**
- Setup & config: 30 min
- User model + tests: 1 hour
- Serializers + tests: 45 min
- API endpoints + tests: 1.5 hours
- Manual testing: 30 min
- Coverage & quality: 30 min
- Commit & document: 15 min

---

## ✅ Success Criteria

- [ ] User model created with profile
- [ ] JWT authentication configured
- [ ] 4 working endpoints: signup, login, refresh, logout
- [ ] All endpoints have unit tests
- [ ] Test coverage ≥ 80%
- [ ] Manual testing successful (can register, login, refresh)
- [ ] Code formatted (black, isort)
- [ ] No lint errors (flake8)
- [ ] Committed to feature/habits-mvp branch

---

## 📝 Quick Commands Reference

```bash
# Activate environment
.\venv\Scripts\Activate.ps1

# Run specific test file
pytest backend/core/tests/test_models.py -v

# Run all core tests
pytest backend/core/ -v

# Run with coverage
pytest backend/ --cov=backend --cov-report=term-missing

# Format code
black backend/ && isort backend/ && flake8 backend/

# Run server
cd backend
python manage.py runserver

# Create superuser (for admin access)
python manage.py createsuperuser

# Check Django setup
python manage.py check
```

---

## 🚨 Important Reminders

1. **TDD Approach:** Write tests FIRST, then implement
2. **Branch:** Work on `feature/habits-mvp`, NOT `main`
3. **Coverage:** Minimum 80% for all new code
4. **Tests:** Must pass before committing
5. **Format:** Run black/isort/flake8 before commit

---

## 📚 Resources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [SimpleJWT Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [pytest-django Docs](https://pytest-django.readthedocs.io/)
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) (local reference)

---

**Ready to build! Start with creating the branch, then TDD all the way.** 🚀
