-- Copyright (c) 2013 cupdir
-- RPM版本源管理API
--提供针对版本号查询，时间维度的查询，RPM包上传，消息回执。
require 'ngx_core_upload'
local api = { funcs={} }
api.__index = api

function api.__call(api, value)
	return api:new(value)
end
function api:new(value, chained)
	return setmetatable({ _val = value, chained = chained or false }, self)
end
function api.identity(value)
	return value
end
function api:chain()
	self.chained = true
	return self
end

function api:value()
	return self._val
end

-- class method start 
-- 上传RPM 包， 检测POST数据md5hash值是否存在，如果存在执行上传操作，上传完成执行MD5校验
-- @author cupdir
-- @param 
-- @return boolen
function api.funcs.upload(...)

	return '111'
end

--class  method end

function api.functions() 
	return api.keys(api.funcs)
end
-- 别名
api.methods = api.functions
-- 获取rpm的md5sum值
--param string rpm_path
local function wrap_functions_for_oo_support()
	local function value_and_chained(value_or_self)
		local chained = false
		if getmetatable(value_or_self) == api then 
			chained = value_or_self.chained
			value_or_self = value_or_self._val 
		end
		return value_or_self, chained
	end

	local function value_or_wrap(value, chained)
		if chained then value = api:new(value, true) end
		return value
	end

	for fn, func in pairs(api.funcs) do
		api[fn] = function(obj_or_self, ...)
			local obj, chained = value_and_chained(obj_or_self)	
			return value_or_wrap(func(obj, ...), chained)		
		end	 
	end
end
wrap_functions_for_oo_support()
return api:new()