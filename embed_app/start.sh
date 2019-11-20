/opt/setdns.sh

create_ap --config /etc/create_ap.conf &

/usr/local/nginx/sbin/nginx &


PATH=/opt/qt_sdk/bin:$PATH
export PATH

LD_LIBRARY_PATH=/opt/qt_sdk/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

export QT_PLUGIN_PATH=/opt/qt_sdk/plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/opt/qt_sdk/plugins/platforms

cd /opt/NanoPI-R1 
python3 serial2db.py &

cd /opt/webpy
python3 code.py & 
