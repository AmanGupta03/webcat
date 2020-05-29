
cd /
echo "root dir"
cd home/ec2-user/webcat
echo "correct dir"
. venv/bin/activate
echo "Server terminal Started"
/usr/bin/nohup python3 app.py &
echo "Server Started ..."
deactivate
sleep 10
sudo killall chrome
sudo killall chromedriver
echo "Script completed"
