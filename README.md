# Subversion 搭建
支持 https,http,443三种检出方式。同意
#安装 subversion
	http://mirror.bit.edu.cn/apache/subversion/
	wget http://mirror.bit.edu.cn/apache/subversion/subversion-1.7.9.tar.gz
	tar zxvf subversion-1.7.9
	cd subversion-1.7.9
	./configure  --prefix=/usr/local/subversion-1.7.9 --with-apxs=/apache/httpd/bin/apxs --with-apr=/usr/local/apr/bin/apr-1-config --with-apr-util=/usr/local/apr/bin/apu-1-config --without-serf --without-neon
	make 
	make install
#创建版本库
	mkdir /data/svn
	mkdir /data/svn/repos
#执行数据存储为 FSFS
	svnadmin create --fs-type fsfs /data/svn/repos
#服务端启动
	svnserve –d -r /data/svn --log-file=/data/logs/svn_logs/svn.log  --listen-port=17800
#在线书籍
http://www.subversion.org.cn/svnbook/1.4/svnbook.html#svn.serverconfig.choosing.svn-ssh
#apache 安装  openssl
##下载openssl

	http://www.openssl.org/source/
	wget http://www.openssl.org/source/openssl-1.0.1e.tar.gz
	tar zxvf openssl-1.0.1e.tar.gz
	cd openssl-1.0.1e
	./config --prefix=/usr/local zlib-dynamic --openssldir=/etc/ssl shared
	make
	make install
## pcre 安装
	http://pcre.org/
	wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.21.tar.gz
	tar zxvf pcre-8.21.tar.gz
	./configure
	make 
	make install
## apr安装
	http://mirrors.ustc.edu.cn/gnu/libtool/
	wget http://apache.mesi.com.ar/apr/apr-1.4.6.tar.gz
	tar zxvf apr-1.4.6.tar.gz
	mv apr-1.4.6 httpd-2.4.4/srclib/apr

## apr-util安装
	wget http://mirror.bit.edu.cn/apache/apr/apr-util-1.5.2.tar.gz
	tar zxvf apr-util-1.5.2.tar.gz
	mv apr-util-1.5.2 httpd-2.4.4/srclib/apr-util

## apache 安装

	http://httpd.apache.org/download.cgi#apache24
	wget http://mirror.bit.edu.cn/apache/httpd/httpd-2.4.4.tar.gz
	tar zxvf httpd-2.4.4.tar.gz
	./configure --prefix=/apache/httpd --enable-so --enable-ssl=static --enable-mods-shared=all  --with-ssl=/usr/local/ssl --enable-dav --enable-dav-fs --with-ldap --with-ldap-include=/usr/lib64/evolution-openldap/include/ --with-ldap-lib=/usr/lib64/ --enable-ldap --enable-authnz-ldap  --with-included-apr  --enable-authn-alias 
	make install
	cp /apache/httpd/bin/apachectl /etc/rc.d/init.d/httpd
	chmod 755 /etc/rc.d/init.d/httpd
## 制作证书
	wget http://www.openssl.org/contrib/ssl.ca-0.1.tar.gz
	cp ssl.ca-0.1.tar.gz /apache/httpd/conf
	cd /apache/httpd/conf/
	tar zxvf ssl.ca-0.1.tar.gz
	./configure
	make 
	make install

	cp ssl.ca-0.1.tar.gz /apache/httpd/conf
	cd /apache/httpd/conf
	tar zxvf ssl.ca-0.1.tar.gz
	cd ssl.ca-0.1
	./new-root-ca.sh

	Enter pass phrase for ca.key: (输入一个密码)
	Verifying - Enter pass phrase for ca.key: (再输入一次密码)

	Enter pass phrase for ca.key: (输入刚刚设置的密码)

	./sign-server-cert.sh server
	Enter pass phrase for ./ca.key: (输入上面设置的根证书密码)

	chmod 400 server.key
	cd ..
	mkdir ssl.key
	mv ssl.ca-0.1/server.key ssl.key
	mkdir ssl.crt
	mv ssl.ca-0.1/server.crt ssl.crt
	然后就可以启动啦！
	cd /apache/httpd
	./bin/apachectl start


A机器		
cd
ssh-keygen -t dsa -b 1024 -f /root/this-host-rsync-key
cp this-host-rsync-* ~/.ssh
scp this-host-rsync-key.pub root@191.168.0.11:/root/.ssh/

B机器
cd ~/.ssh/
cat this-host-rsync-key.pub > authorized_keys

