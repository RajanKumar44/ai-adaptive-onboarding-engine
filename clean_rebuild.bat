@echo off
REM Complete Docker cleanup and rebuild script

echo ============== STEP 1: STOPPING ALL CONTAINERS ==============
docker stop $(docker ps -q) 2>nul
timeout /t 3 /nobreak

echo.
echo ============== STEP 2: REMOVING ALL CONTAINERS ==============
docker rm $(docker ps -aq) 2>nul
timeout /t 3 /nobreak

echo.
echo ============== STEP 3: REMOVING ALL IMAGES ==============
docker rmi $(docker images -q) 2>nul
timeout /t 3 /nobreak

echo.
echo ============== STEP 4: REMOVING ALL VOLUMES ==============
docker volume prune -f 2>nul
timeout /t 3 /nobreak

echo.
echo ============== STEP 5: SYSTEM CLEANUP ==============
docker system prune -a -f --volumes 2>nul
timeout /t 3 /nobreak

echo.
echo ============== STEP 6: NAVIGATE TO BACKEND ==============
cd /d c:\Users\Rajan\OneDrive\Desktop\ai-adaptive-onboarding-engine-main\backend

echo.
echo ============== STEP 7: BUILD FROM SCRATCH ==============
docker-compose build --no-cache

echo.
echo ============== STEP 8: START CONTAINERS ==============
docker-compose up -d

echo.
echo ============== STEP 9: WAITING FOR INITIALIZATION (30 seconds) ==============
timeout /t 30 /nobreak

echo.
echo ============== STEP 10: CHECKING LOGS ==============
docker logs ai-onboarding-app --tail 100

echo.
echo ============== CLEANUP AND BUILD COMPLETE ==============
pause
