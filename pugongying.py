# coding=utf-8

"""
    * User:  answer.huang
    * Email: aihoo91@gmail.com
    * Date:  15/3/31
    * Time:  18:33
    * Blog:  answerhuang.duapp.com
    """

import time
import urllib2
import time
import json
import mimetypes
import os
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

import json

#蒲公英应用上传地址
url = 'http://www.pgyer.com/apiv1/app/upload'
#蒲公英提供的 用户Key
uKey = '**********'
#上传文件的文件名（这个可随便取，但一定要以 ipa 结尾）
file_name = '**********.ipa'
#蒲公英提供的 API Key
_api_key = '**********'
#安装应用时需要输入的密码，这个可不填
installPassword = '111111'

# 运行时环境变量字典
environsDict = os.environ
#此次 jenkins 构建版本号
jenkins_build_number = environsDict['BUILD_NUMBER']

#项目名称，用在 拼接 tomcat 文件地址
project_name = 'ios_user_client'

#ipa 文件在 tomcat 服务器上的地址
ipa_file_tomcat_http_url = 'http://192.168.16.221:8080/' + project_name + '/static/' + jenkins_build_number + '/' + jenkins_build_number + '.ipa'

#获取 ipa 文件路径
def get_ipa_file_path():
    #工作目录下面的 ipa 文件
    ipa_file_workspace_path = '/Users/eku/.jenkins/jobs/' + project_name + '/workspace/build/' + jenkins_build_number + '.ipa'
    #tomcat 上的 ipa 文件
    ipa_file_tomcat_path = '/usr/local/tomcat/webapps/' + project_name + '/static/' + jenkins_build_number + '/' + jenkins_build_number + '.ipa'
    
    if os.path.exists(ipa_file_workspace_path):
        return ipa_file_workspace_path
    elif os.path.exists(ipa_file_tomcat_path):
        return ipa_file_tomcat_path

# while get_ipa_file_path() is None:
#     time.sleep(5)

#ipa 文件路径
ipa_file_path = get_ipa_file_path()
print ipa_file_path

#请求字典编码
def _encode_multipart(params_dict):
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in params_dict.items():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            filename = getattr(v, 'name', '')
            content = v.read()
            decoded_content = content.decode('ISO-8859-1')
            data.append('Content-Disposition: form-data; name="%s"; filename="kangda.ipa"' % k)
            data.append('Content-Type: application/octet-stream\r\n')
            data.append(decoded_content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v if isinstance(v, str) else v.decode('utf-8'))
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary


#处理 蒲公英 上传结果
def handle_resule(result):
    json_result = json.loads(result)
    if json_result['code'] is 0:
        send_Email(json_result)

#发送邮件
def send_Email(json_result):
    appName = json_result['data']['appName']
    appKey = json_result['data']['appKey']
    appVersion = json_result['data']['appVersion']
    appBuildVersion = json_result['data']['appBuildVersion']
    appShortcutUrl = json_result['data']['appShortcutUrl']
    #邮件接受者
    mail_receiver = ['aihoo91@gmail.com']
    #根据不同邮箱配置 host，user，和pwd
    mail_host = '**********'
    mail_user = '**********'
    mail_pwd = '**********'
    mail_to = ','.join(mail_receiver)
    
    msg = MIMEMultipart()
    
    environsString = '<h3>本次打包相关信息</h3><p>'
    environsString += '<p>ipa 包下载地址 : ' + ipa_file_tomcat_http_url + '<p>'
    environsString += '<p>你也可从蒲公英网站在线安装 : ' + 'http://www.pgyer.com/' + str(appShortcutUrl) + '   密码 : ' + installPassword + '<p>'
    environsString += '<li><a href="itms-services://?action=download-manifest&url=https://ssl.pgyer.com/app/plist/' + str(appKey) + '">点我直接安装</a></li>'
    message = environsString
    body = MIMEText(message, _subtype='html', _charset='utf-8')
    msg.attach(body)
    msg['To'] = mail_to
    msg['from'] = mail_user
    msg['subject'] = '最新打包文件'
    
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pwd)
        
        s.sendmail(mail_user, mail_receiver, msg.as_string())
        s.close()
        
        print 'success'
    except Exception, e:
        print e

#############################################################
#请求参数字典
params = {
    'uKey': uKey,
    '_api_key': _api_key,
    'file': open(ipa_file_path, 'rb'),
    'publishRange': '2',
    'password': installPassword

}

coded_params, boundary = _encode_multipart(params)
req = urllib2.Request(url, coded_params.encode('ISO-8859-1'))
req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
try:
    resp = urllib2.urlopen(req)
    body = resp.read().decode('utf-8')
    handle_resule(body)

except urllib2.HTTPError as e:
    print(e.fp.read())







