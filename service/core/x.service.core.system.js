var plugins = require('./plugins/x.service.core.plugins.svn'),
	events = require('events'),
	EventEmitter = events.EventEmitter,
	sys = require('sys');
//定义system
function system(){
	
	EventEmitter.call(this);
};
sys.inherits(system, EventEmitter);
//svn class
system.prototype.svn = plugins.svn;

exports.system = new system();



