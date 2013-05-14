(function (exports, global) {

  /**
   * 工具包命名 namespace.
   *
   * @namespace
   */

  var util = exports.util = {};

  /**
   * Parses an URI
   * @api public
   */

  var re = /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/;

  var parts = ['source', 'protocol', 'authority', 'userInfo', 'user', 'password',
               'host', 'port', 'relative', 'path', 'directory', 'file', 'query',
               'anchor'];

  util.parseUri = function (str) {
    var m = re.exec(str || '')
      , uri = {}
      , i = 14;

    while (i--) {
      uri[parts[i]] = m[i] || '';
    }

    return uri;
  };
util.zero = function(bit,max){
  var length = bit.toString().length;
    while(length < max) {
        bit = "0" + bit;
        length++;
    }
    return bit.toString();
};
  /**
   * @param {Object} uri
   * @api public
   */

  util.uniqueUri = function (uri) {
    var protocol = uri.protocol
      , host = uri.host
      , port = uri.port;

    if ('document' in global) {
      host = host || document.domain;
      port = port || (protocol == 'https'
        && document.location.protocol !== 'https:' ? 443 : document.location.port);
    } else {
      host = host || 'localhost';

      if (!port && protocol == 'https') {
        port = 443;
      }
    }

    return (protocol || 'http') + '://' + host + ':' + (port || 80);
  };

  /**
   * @param {String} base
   * @param {String} addition
   * @api public
   */

  util.query = function (base, addition) {
    var query = util.chunkQuery(base || '')
      , components = [];

    util.merge(query, util.chunkQuery(addition || ''));
    for (var part in query) {
      if (query.hasOwnProperty(part)) {
        components.push(part + '=' + query[part]);
      }
    }

    return components.length ? '?' + components.join('&') : '';
  };

  /**
   * @param {String} qs
   * @api public
   */

  util.chunkQuery = function (qs) {
    var query = {}
      , params = qs.split('&')
      , i = 0
      , l = params.length
      , kv;

    for (; i < l; ++i) {
      kv = params[i].split('=');
      if (kv[0]) {
        query[kv[0]] = kv[1];
      }
    }

    return query;
  };

  /**
   * @param {Function} fn
   * @api public
   */

  var pageLoaded = false;

  util.load = function (fn) {
    if ('document' in global && document.readyState === 'complete' || pageLoaded) {
      return fn();
    }

    util.on(global, 'load', fn, false);
  };

  /**
   * 监听一个自定义事件
   *
   * @api private
   */

  util.on = function (element, event, fn, capture) {
    if (element.attachEvent) {
      element.attachEvent('on' + event, fn);
    } else if (element.addEventListener) {
      element.addEventListener(event, fn, capture);
    }
  };

  util.request = function (xdomain) {
    var XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;
    return new XMLHttpRequest();

    if (xdomain && 'undefined' != typeof XDomainRequest && !util.ua.hasCORS) {
      return new XDomainRequest();
    }

    if ('undefined' != typeof XMLHttpRequest && (!xdomain || util.ua.hasCORS)) {
      return new XMLHttpRequest();
    }

    if (!xdomain) {
      try {
        return new ActiveXObject('Microsoft.XMLHTTP');
      } catch(e) { }
    }

    return null;
  };

  if ('undefined' != typeof window) {
    util.load(function () {
      pageLoaded = true;
    });
  }

  util.defer = function (fn) {
    if (!util.ua.webkit || 'undefined' != typeof importScripts) {
      return fn();
    }

    util.load(function () {
      setTimeout(fn, 100);
    });
  };

  /**
   * 合并两个对象.
   *
   * @api public
   */

  util.merge = function merge (target, additional, deep, lastseen) {
    var seen = lastseen || []
      , depth = typeof deep == 'undefined' ? 2 : deep
      , prop;

    for (prop in additional) {
      if (additional.hasOwnProperty(prop) && util.indexOf(seen, prop) < 0) {
        if (typeof target[prop] !== 'object' || !depth) {
          target[prop] = additional[prop];
          seen.push(additional[prop]);
        } else {
          util.merge(target[prop], additional[prop], depth - 1, seen);
        }
      }
    }

    return target;
  };
  //合并数据
  util.array_merge = function(){
    var args = Array.prototype.slice.call(arguments),
            retObj = {},
            k, j = 0,        i = 0,
            retArr = true;
     
        for (i = 0; i < args.length; i++) {
            if (!(args[i] instanceof Array)) {            retArr = false;
                break;
            }
        }
         if (retArr) {
            retArr = [];
            for (i = 0; i < args.length; i++) {
                retArr = retArr.concat(args[i]);
            }        return retArr;
        }
        var ct = 0;
     
        for (i = 0, ct = 0; i < args.length; i++) {        if (args[i] instanceof Array) {
                for (j = 0; j < args[i].length; j++) {
                    retObj[ct++] = args[i][j];
                }
            } else {            
              for (k in args[i]) {
                    if (args[i].hasOwnProperty(k)) {
                        if (parseInt(k, 10) + '' === k) {
                            retObj[ct++] = args[i][k];
                        } else {                        retObj[k] = args[i][k];
                        }
                    }
                }
            }    }
        return retObj;    
  };
  /**
   * Merges prototypes from objects
   *
   * @api public
   */

  util.mixin = function (ctor, ctor2) {
    util.merge(ctor.prototype, ctor2.prototype);
  };

  util.inherit = function (ctor, ctor2) {
    function f() {};
    f.prototype = ctor2.prototype;
    ctor.prototype = new f;
  };
  util.format=function(fmt) {
        time = new Date();      
        var o = {        
        "M+" : time.getMonth()+1, //月份        
        "d+" : time.getDate(), //日        
        "h+" : time.getHours()%12 == 0 ? 12 : time.getHours()%12, //小时        
        "H+" : time.getHours(), //小时        
        "m+" : time.getMinutes(), //分        
        "s+" : time.getSeconds(), //秒        
        "q+" : Math.floor((time.getMonth()+3)/3), //季度        
        "S" : time.getMilliseconds() //毫秒        
        };        
        var week = {        
        "0" : "\u65e5",        
        "1" : "\u4e00",        
        "2" : "\u4e8c",        
        "3" : "\u4e09",        
        "4" : "\u56db",        
        "5" : "\u4e94",        
        "6" : "\u516d"       
        };        
        if(/(y+)/.test(fmt)){        
            fmt=fmt.replace(RegExp.$1, (time.getFullYear()+"").substr(4 - RegExp.$1.length));        
        }        
        if(/(E+)/.test(fmt)){        
            fmt=fmt.replace(RegExp.$1, ((RegExp.$1.length>1) ? (RegExp.$1.length>2 ? "\u661f\u671f" : "\u5468") : "")+week[this.getDay()+""]);        
        }        
        for(var k in o){        
            if(new RegExp("("+ k +")").test(fmt)){        
                fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));        
            }        
        }        
        return fmt;        
  };
  util.isArray = Array.isArray || function (obj) {
    return Object.prototype.toString.call(obj) === '[object Array]';
  };

  util.intersect = function (arr, arr2) {
    var ret = []
      , longest = arr.length > arr2.length ? arr : arr2
      , shortest = arr.length > arr2.length ? arr2 : arr;

    for (var i = 0, l = shortest.length; i < l; i++) {
      if (~util.indexOf(longest, shortest[i]))
        ret.push(shortest[i]);
    }

    return ret;
  };

  util.indexOf = function (arr, o, i) {

    for (var j = arr.length, i = i < 0 ? i + j < 0 ? 0 : i + j : i || 0;
         i < j && arr[i] !== o; i++) {}

    return j <= i ? -1 : i;
  };

  util.toArray = function (enu) {
    var arr = [];

    for (var i = 0, l = enu.length; i < l; i++)
      arr.push(enu[i]);

    return arr;
  };

  /**
   * UA / engines detection namespace.
   *
   * @namespace
   */

  util.ua = {};

  /**
   * Whether the UA supports CORS for XHR.
   *
   * @api public
   */

  util.ua.hasCORS = 'undefined' != typeof XMLHttpRequest && (function () {
    try {
      var a = new XMLHttpRequest();
    } catch (e) {
      return false;
    }

    return a.withCredentials != undefined;
  })();

  /**
   * Detect webkit.
   *
   * @api public
   */

  util.ua.webkit = 'undefined' != typeof navigator
    && /webkit/i.test(navigator.userAgent);

   /**
   *  iPad/iPhone/iPod.
   *
   * @api public
   */

  util.ua.iDevice = 'undefined' != typeof navigator
      && /iPad|iPhone|iPod/i.test(navigator.userAgent);

})('undefined' != typeof io ? io : module.exports, this);
