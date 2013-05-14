/**
  +------------------------------------------------------------------------------
 * RPM文件转存 服务端
  +------------------------------------------------------------------------------
 * @author   cupdir <cupdir@gmail.com>
 * @version  $Id$
  +------------------------------------------------------------------------------
 */
var util 	= 	require('./lib/util').util,	//工具包
	events	=	require('events'),//让本类继承event
	http 	=	require('http'),
	url 	= require('url'),
	querystring = require('querystring'); //解析POST数据
/*
	#接收nginx_upload_module模块的上传状态，验证上传文件的token
*/
function upload(config){
	//版本号
	this.version = '0.0.1';
	//配置选项 tables
	this.config = config;
	events.EventEmitter.call(this);
};
util.inherit(upload, events.EventEmitter); 
upload.prototype.http = function(){
	var self = this;
	var proxy = http.createServer(function (req, res){
		var post='';
		req.setEncoding('utf8');
		req.addListener('data',function(data){
			post += data; //解析post数据
			//self.uploadProcess();//上传进度反馈
			console.log('[Received]' + data.length);
			//post
		});
		req.addListener('end',function(){
			req.post = querystring.parse(post);
			req.get = url.parse(req.url, true).query;
			if( req.method.toLowerCase() == 'post' ){
				console.log(req.get);
				res.writeHead(200, {'Content-Type': 'application/json; charset=utf-8'});
				res.end(JSON.stringify(req.get));
			}else{
				//405 Method Not Allowed
				res.writeHead(405, {'Content-Type': 'text/plain'});
				res.end();				
			}
		});
	});
	proxy.on('error',function(err){
		console.log('(6)端口'+self.config.port+'开启失败');
		process.exit(1);

	})
	proxy.listen(this.config.port,function(){
		console.log('(6)端口'+self.config.port+'开启成功.'); 
	});
};

//开启服务，对外提供一个HTTP接口
upload.prototype.start = function(){
	var self = this;
	console.log('(1)开启http服务');
	this.http();//创建交互请求
};
var config =  {
				port:8080
			};
var uploadService =  new upload(config);
uploadService.start(); //开启服务