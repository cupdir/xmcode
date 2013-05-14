import redis
import os
import commands
import time
import json
import sys
import pycurl
import random
from daemon import Daemon

class MiUp(Daemon):
    rootpath = '/home/xiaoqing/work/xmcode/sbin/' #FIXME
    rpmbuildpath = '/usr/src/rpmbuild/'
    redis_host = '10.237.93.17'
    redis_port = 6379
    upload_srv = 'http://rpmapi.b2c.srv/upload'

    rds = redis.Redis(host = redis_host, port = redis_port, db = 0)

    #TODO write logs and error handling
    def run(self):
        while (True):

            task = self.rds.lpop('miup_task_' + self.queue_id)
            print 'miup_task_' + self.queue_id
            if not task:
                print 'No task'
                time.sleep(1)
                continue
            self.writelog('[INFO] Task #' + task_info['task_id'] + ' begin..')
            #Step1: floder 'rep/xxx' update to the release version
            print '---up---'
            status, output = self.up_to_version(task_info, task_info['release_ver'])
            if status != 0:
                self.writelog('[FAILED] up to version failed: ' + output)
                self.rds.lpush('miup_task_' + self.queue_id) #FIXME error handling
                continue

            #Step2: rsync folder 'rpmsrc/xxx'
            print '---rsync---'
            status, output = self.rsync(task_info['release_exclude'])
            if status != 0:
                self.writelog('[FAILED] rsync folder failed: ' + output)
                self.rds.lpush('miup_task_' + self.queue_id) #FIXME error handling
                continue

            #Step3: make xxx.tar.gz
            srcpath = 'rpmsrc/' + task_info['project_id']
            project_name = task_info['project_name']
            tarversion = task_info['task_id']
            print '---mktar---'
            status, output = self.mktar(srcpath, project_name + '-' + tarversion)
            if status != 0:
                self.writelog('[FAILED] make tar.gz failed: ' + output)
                self.rds.lpush('miup_task_' + self.queue_id) #FIXME error handling
                continue

            #Step4 make spec file
            print '---mkspec---'
            status, output = self.mkspec(project_name, tarversion, task_info['release_server']['path'])
            if status != 0:
                self.writelog('[FAILED] make spec file failed: ' + output)
                self.rds.lpush('miup_task_' + self.queue_id) #FIXME error handling
                continue
            #Step5 make xxx.rpm
            print '---rpmbuild---'
            status, output = self.rpmbuild(project_name + '-' + tarversion)
            if status != 0:
                self.writelog('[FAILED] make rpm package failed: ' + output)
                self.rds.lpush('miup_task_' + self.queue_id) #FIXME error handling
                continue

            #Step6: upload to the package server
            print '---upload---'
            status, output = self.upload(self.rpmbuildpath + '/RPMS/' + project_name + '-' + tarversion + '.rpm')
            if status != 0:
                self.writelog('[FAILED] upload rpm package failed: ' + output)
            self.writelog('[INFO] Task #' + task_info['task_id'] + ' finished.')

    def mkspec(self, project_name, tarversion, destdir):
        try:
            with open('base_spec_tpl', 'r') as tpl, open(self.rpmbuildpath + 'SPECS/' + project_name + '-' + tarversion + '.spec', 'w') as f:
                content = tpl.read() % (project_name, tarversion, destdir)
                f.write(content)
                self.writelog('[INFO] make ' + self.rpmbuildpath + 'SPECS/' + project_name + '-' + tarversion + '.spec')
                return 0, None
        except IOError as ioerr:
            return 1, str(ioerr)

    def mktar(self, srcpath, tarname):
        cmd = 'cp -r ' + srcpath + ' ' + self.rpmbuildpath + 'SOURCES/' + tarname
        cmd += '; cd ' + self.rpmbuildpath + 'SOURCES; tar zcf ' + tarname + '.tar.gz ' + tarname
        cmd += '; rm -rf ' + tarname
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def rpmbuild(self, tarname):
        #TODO: VERIFY SPEC file and tgz file
        cmd = "rpmbuild -ba " + self.rpmbuildpath + 'SPECS/' + tarname + '.spec'
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def checkout_svn(self, task_info, version):
        cmd_version = ""
        if version != 0:
            cmd_version = ' -r ' + version
        cmd = "svn co -q " + cmd_version + " " + task_info['rep_proto']+ "://" +\
                task_info['rep_host'] + ":" + task_info['rep_port'] + "/" + task_info['rep_path'] +\
                " --username " + task_info['rep_user'] + " --password " + task_info['rep_pass'] +\
                " --no-auth-cache --non-interactive rep/" + task_info['project_id'] +\
                " > /dev/null 2>&1"
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def update_svn(self, task_info, version = 0):
        cmd_version = ""
        if version != 0:
            cmd_version = ' -r ' + version
        cmd = "svn up -q " + cmd_version + " --no-auth-cache --non-interactive rep/" + task_info['project_id'] + " > /dev/null 2>&1"
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def svn_up_to_version(self, task_info, version):
        path = "rep/" + task_info['project_id']
        if os.path.exists(path):
            self.writelog('[INFO] svn update')
            return self.update_svn(task_info, version)
        else:
            self.writelog('[INFO] svn checkout')
            return self.checkout_svn(task_info, version)

    def git_up_to_version(self, task_info, version): #######################FIXME
        path = "rep/" + task_info['project_id']
        if os.path.exists(path):
            self.writelog('[INFO] git pull')
            cmd = "git pull"
        else:
            self.writelog('[INFO] git clone')
            cmd = "git clone " + task_info['rep_proto'] + "://" + task_info['rep_user'] + "@" + task_info['rep_host'] + ":" + task_info['rep_port'] + "/" + task_info['rep_name'] + " rep/" + task_info['project_id']
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        #TODO ?? clone and checkout???
        if status:
            return status,project_id
        os.chdir(self.rootpath)
        os.chdir(path)
        cmd = "git checkout " + task_info['release_ver']
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output


    def up_to_version(self, task_info, version):
        if task_info['rep_type'] == "git":
            self.writelog('[INFO] git project')
            return self.git_up_to_version(task_info, version)
        elif task_info['rep_type'] == 'svn':
            self.writelog('[INFO] svn project')
            return self.svn_up_to_version(task_info, version)
        else:
            self.writelog('[ERROR] unknown type project')
            return 1, 'unknown type'

    def rsync(self, exclude_path):
        if not os.path.exists('rpmsrc'):
            os.mkdir('rpmsrc')
        exclude_cmd = " --exclude='.git' --exclude='.gitignore' --exclude='.svn'"
        for path in exclude_path:
            exclude_cmd += " --exclude='" + path + "'"
        cmd = "rsync -rlt --timeout=300 " + exclude_cmd + " rep/" + task_info['project_id'] + "/ rpmsrc/" + task_info['project_id']
        self.writelog('[INFO] cmd: ' + cmd)
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def upload0(self, filepath):
        if not os.path.exists(filepath):
            return 1, 'file not exist'
        cmd = 'md5sum ' + filepath
        status, output = commands.getstatusoutput(cmd)
        md5sum = output.split(' ')[0]
        cmd = 'curl -v -i -XPOST ' + self.upload_srv + '?token=' + md5sum + ' -F "media=@' + filepath + ';type=application/octet-stream;filename=' + filepath.split('/')[-1] + '"'
        status, output = commands.getstatusoutput(cmd)
        return status, output

    def upload(self, filepath):
        if not os.path.exists(filepath):
            self.writelog('[ERROR] rpm file not exist')
            return 1, 'file not exist'
        cmd = 'md5sum ' + filepath
        c = pycurl.Curl()
        status, output = commands.getstatusoutput(cmd)
        md5sum = output.split(' ')[0]
        xpid = md5sum + self.gen_random(6)
        c.setopt(c.POST, 1)
        c.setopt(c.URL, self.upload_srv)
        self.writelog('[INFO] upload: token=' + md5sum)
        self.writelog('[INFO] upload: X-Progress-ID=' + xpid)
        post_filed = [(filepath.split('/')[-1], (c.FORM_FILE, filepath)),
                      ('token', (c.FORM_CONTENTS, md5sum)),
                      ('X-Progress-ID', (c.FORM_CONTENTS, xpid))]
        c.setopt(c.HTTPPOST, post_filed)
        try:
            c.perform()
            if c.getinfo(pycurl.HTTP_CODE) != 200: #FIXME
                self.writelog('[FAILED] upload: pycurl.HTTP_CODE=' + str(pycurl.HTTP_CODE))
                return 2, 'pycurl failed'
            return 0, 'SUCCESS'
        except pycurl.error, err:
            self.writelog('[FAILED] upload: ' + err)
            return 3, err
        finally:
            c.close()

    def gen_random(self, length):
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.sample(chars, length))

    def writelog(self, msg):
        print msg
        date_tag = time.strftime('%Y%m%d', time.localtime(time.time()))
        time_tag = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
        f = open(self.rootpath + "logs/" + date_tag + '.log','a')
        f.write(time_tag + " " + msg + "\n")
        f.close()


if __name__ == "__main__":

    daemon = MiUp('/tmp/miup_py.pid')
    #task data struct
    task_info = {}
    task_info['task_id'] = '10112'
    task_info['rep_host'] = 'b2code.xiaomi.com'
    task_info['rep_port'] = '443'
    task_info['rep_path'] = '/repos/10.xiaomi.com/'
    task_info['rep_user'] = 'wanghaiquan'
    task_info['rep_pass'] = 'haiquan82@186'
    task_info['rep_type'] = 'svn'
    task_info['rep_proto'] = 'https'
    task_info['project_id'] = '10001'
    task_info['project_name'] = '10.xiaomi.com'
    task_info['rsync_delete'] = '0'
    task_info['release_root'] = '/'
    task_info['release_exclude'] = ['/js/', '/none.txt', '/robots.txt', '/t.html']
    task_info['release_push'] = '0'
    task_info['release_thread'] = '15'
    task_info['release_restart'] = '0'
    task_info['release_rescript'] = ''
    task_info['release_ver'] = '32'
    task_info['current_ver'] = '30'
    task_info['release_server'] = {}
    task_info['release_server']['ip'] = '10.237.93.43'
    task_info['release_server']['port'] = '22'
    task_info['release_server']['path'] = '/data/www/10.xiaomi.com'

    if len(sys.argv) > 2:
        daemon.queue_id = sys.argv[1]
    else:
        daemon.queue_id = 'comm'
    daemon.rds.lpush('miup_task_' + daemon.queue_id, task_info)
    
    daemon.run()
    #if len(sys.argv) > 2:
    #    if 'start' == sys.argv[1]:
    #        daemon.start()
    #    elif 'stop' == sys.argv[1]:
    #        daemon.stop()
    #    elif 'restart' == sys.argv[1]:
    #        daemon.restart()
    #    else:
    #        print "Unknown command"
    #        sys.exit(2)
    #    sys.exit(0)
    #else:
    #    print "usage: %s {start|stop|restart}" % sys.argv[0]
    #    sys.exit(2)
