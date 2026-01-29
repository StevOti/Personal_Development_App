# Manual API Testing Script for JWT Authentication
# Week 1 - Authentication System Test

Write-Host ""
Write-Host "=== Testing JWT Authentication System ===" -ForegroundColor Cyan

# Test 1: Signup
Write-Host ""
Write-Host "1. Testing Signup..." -ForegroundColor Yellow
$signupBody = @{
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"
    password2 = "testpass123"
} | ConvertTo-Json

try {
    $signupResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/signup/" `
        -Method Post `
        -Body $signupBody `
        -ContentType "application/json"
    
    Write-Host "Signup successful!" -ForegroundColor Green
    Write-Host "User:" $signupResponse.user.username -ForegroundColor White
    
    $accessToken = $signupResponse.access
    $refreshToken = $signupResponse.refresh
} catch {
    Write-Host "Signup failed:" $_ -ForegroundColor Red
    exit 1
}

# Test 2: Login
Write-Host ""
Write-Host "2. Testing Login..." -ForegroundColor Yellow
$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    Write-Host "Login successful!" -ForegroundColor Green
    
    $accessToken = $loginResponse.access
    $refreshToken = $loginResponse.refresh
} catch {
    Write-Host "Login failed:" $_ -ForegroundColor Red
}

# Test 3: Token Refresh
Write-Host ""
Write-Host "3. Testing Token Refresh..." -ForegroundColor Yellow
$refreshBody = @{
    refresh = $refreshToken
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/refresh/" `
        -Method Post `
        -Body $refreshBody `
        -ContentType "application/json"
    
    Write-Host "Token refresh successful!" -ForegroundColor Green
    
    $newAccessToken = $refreshResponse.access
    $newRefreshToken = $refreshResponse.refresh
} catch {
    Write-Host "Token refresh failed:" $_ -ForegroundColor Red
}

# Test 4: Logout
Write-Host ""
Write-Host "4. Testing Logout..." -ForegroundColor Yellow
$logoutBody = @{
    refresh = $newRefreshToken
} | ConvertTo-Json

try {
    $logoutResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/logout/" `
        -Method Post `
        -Body $logoutBody `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $newAccessToken"}
    
    Write-Host "Logout successful!" -ForegroundColor Green
} catch {
    Write-Host "Logout failed:" $_ -ForegroundColor Red
}

# Test 5: Try using blacklisted token
Write-Host ""
Write-Host "5. Testing Blacklisted Token (should fail)..." -ForegroundColor Yellow
$blacklistedRefreshBody = @{
    refresh = $newRefreshToken
} | ConvertTo-Json

try {
    $blacklistedResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/refresh/" `
        -Method Post `
        -Body $blacklistedRefreshBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "PROBLEM: Blacklisted token still works!" -ForegroundColor Red
} catch {
    Write-Host "Correctly rejected blacklisted token!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== All tests complete ===" -ForegroundColor Cyan
