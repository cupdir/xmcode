error_log  /dev/stderr warn;
daemon off;
worker_processes 4;
pid /tmp/nginx-big-upload-test.pid;

events {
	worker_connections 10;
}

http {

 server {
   listen 8088;
   server_name localhost;
   access_log /dev/stdout combined;
   error_log /dev/stderr warn;
   client_max_body_size 2048m;

   # unmanaged upload with file_storage_handler - status 201 for all chunks
   location = /upload/resumable {
     lua_code_cache off; #development only
     set $bu_checksum off;
     set $storage file;  #default
     set $file_storage_path /tmp;
     set $package_path '../?.lua';
     content_by_lua_file ../big-upload.lua;
   }

   # backend managed upload with backend_file_storage_handler
   location = /upload/backend {
     lua_code_cache off; #development only
     set $storage backend_file;  #default
     set $bu_checksum off;
     set $file_storage_path /tmp;
     set $backend_url /bknd;
     set $package_path '../?.lua';
     content_by_lua_file ../big-upload.lua;
   }

   #backend managed with crc32 support
   location = /upload/backend-crc32 {
     lua_code_cache off; #development only
     set $storage backend_file;  #default
     set $bu_checksum on;
     set $file_storage_path /tmp;
     set $backend_url /bknd;
     set $package_path '../?.lua';
     content_by_lua_file ../big-upload.lua;
   }



   # setup of lua big-upload for performance tests
   location = /upload/perf-bu {
     gzip off;
     access_log off;
     set $bu_checksum off;
     set $storage backend_file;  #default
     set $file_storage_path /tmp;
     set $backend_url /bknd;
     set $package_path '../?.lua';
     content_by_lua_file ../big-upload.lua;
   }

   # setup of lua big-upload for performance tests
   location = /upload/perf-bu-crc {
     gzip off;
     access_log off;
     set $bu_checksum on;
     set $storage backend_file;  #default
     set $file_storage_path /tmp;
     set $backend_url /bknd;
     set $package_path '../?.lua';
     content_by_lua_file ../big-upload.lua;
   }

   # setup of nginx-upload-module for performance tests
   location = /upload/perf-num {
     gzip off;
     access_log off;
     upload_resumable on;
     upload_pass  /bknd;
     upload_store  /tmp;
     upload_state_store /tmp;
     upload_pass_args off;
     upload_store_access user:rw group:rw;
     upload_buffer_size 512k;
     upload_max_part_header_len 1024;
     upload_set_form_field "name" "$upload_file_name";
     upload_set_form_field "content_type" "$upload_content_type";
     upload_set_form_field "path" "$upload_tmp_path";
     upload_set_form_field "id" "novalue";
   }


   #this is backend experiment to check if lua module can capture named locations
   location /bknd {
     internal;
     access_log off;
     content_by_lua 'ngx.exec("@backend")';
   }

   # backend mock for upload tests, return some header and echoes body input
   location @backend {
     content_by_lua '
        ngx.header["X-Test"]="看到这个说明你上传成功了"
        ngx.header["X-Checksum"]=ngx.req.get_headers()["X-Checksum"]
        ngx.status = 202
        ngx.print(ngx.req.get_body_data()) -- echo request body
     ';
   }

 }
}