./configure --with-http_ssl_module --with-http_stub_status_module --with-syslog  --with-http_lua_module --with-luajit-inc=/usr/local/luajit/include/luajit-2.0/ --with-luajit-lib=/usr/local/luajit/lib/ --add-module=../ngx_devel_kit/ --add-module=../echo-nginx-module/  --with-debug

编辑 Makefile文件，找到ldconfig位置（75行） 
原内容是：LDCONFIG= ldconfig -n 
修改为：LDCONFIG= /sbin/ldconfig -n