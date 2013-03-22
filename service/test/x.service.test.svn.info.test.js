var plugins = require('../core/x.service.core.system.js');
var mocha = require('mocha')
  , Context = mocha.Context
  , Suite = mocha.Suite
  , Test = mocha.Test;
var  assert = require('assert')
 

describe('svn',function(){
  	describe('plugins', function(){
  	 	it('plugins object',function(done){
  	 		console.log(plugins);
  	 		done();
  	 	});
  	 	it('get svn info ', function(done){
	  	 	plugins.system.svn.info('10.xiaomi.com','wanghaiquan','haiquan82@',function(err,data){
	  	 	 	assert(err == null);
	  	 	 	process.nextTick(function(){
	  	 	 		console.log(data);
	  	 	 		
	  	 	 	})
	  	 	 	done();
	  	 	})
  	 	})
  	})
})
