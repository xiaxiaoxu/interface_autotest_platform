#encoding=utf-8
import re
import pickle
import hashlib
import os
import json
import traceback
from .api_request import api_request


#初始化框架工程中的全局变量，存储在测试数据中的唯一值数据
#框架工程中若要使用字典中的任意一个变量，则每次使用后，均需要将字典中的value值进行加1操作。

# os.environ['global_vars'] = {}
proj_path = os.path.dirname(os.path.dirname(__file__))
data_file = os.path.join(proj_path,"config\\staticDataFile")


def get_unique_number_value(unique_number):
    data = None
    try:
        with open(data_file,"rb") as fp:
            var = pickle.load(fp) # 读取pickle序列化字节流文件中内容，反序列化成python的字典对象：{"unique_num1":100,"unique_num2":1000}
            print("字节流文件内容: %s" % var)
            data= var[unique_number] # 获取字典对象中key为unique_number的值
            print("全局唯一数当前生成的值是：%s" %data)
            # global_vars = json.loads(os.environ['global_vars'])
            # print("global_vars: {}".format(global_vars))
            # global_vars[unique_number]=data
            # os.environ['global_vars'] = json.dumps(global_vars)
            # print("os.environ['global_vars']: {}".format(os.environ['global_vars']))
            var[unique_number] +=1 # 把字典对象中key为unique_number的值进行加一操作，以便下提取时保持唯一
        with open(data_file,"wb") as fp:
            pickle.dump(var,fp) # 修改后的字典对象，序列化到字节流文件中
    except Exception as e:
        print("获取测试框架的全局唯一数变量值失败，请求的全局唯一数变量是%s,异常原因如下：%s" %(unique_number,e))
        data = None
    finally:
        return data

def md5(s):
    m5 = hashlib.md5()
    m5.update(s.encode("utf-8"))
    md5_value = m5.hexdigest()
    return md5_value


# 将请求数据中包含的${变量名}的字符串部分，替换为唯一数或者全局变量字典中对应的全局变量
def data_handler(global_key, requestData):
    try:
        if re.search(r"\$\{unique_num\d+\}", requestData):  # 匹配用户名参数，即"${www}"的格式
            var_name = re.search(r"\$\{(unique_num\d+)\}", requestData).group(1)  # 获取用户名参数
            print("var_name:%s" % var_name)
            var_value = get_unique_number_value(var_name)
            print("var_value: %s" % var_value)
            requestData = re.sub(r"\$\{unique_num\d+\}", str(var_value), requestData)
            var_name = var_name.split("_")[1]
            print("var_name: %s" % var_name)
            global_vars = json.loads(os.environ['global_vars'])
            print("global_vars before assignment in data_handler : {}".format(global_vars))
            global_vars[str(global_key)][var_name] = var_value
            print("global_vars after assignment in data_handler : {}".format(global_vars))
            os.environ['global_vars'] = json.dumps(global_vars)
            print("os.environ['global_vars']: {}".format(os.environ['global_vars']))

        if re.search(r"\$\{\w+\(.+\)\}", requestData):  # 匹配密码参数,即"${xxx()}"的格式
            var_pass = re.search(r"\$\{(\w+\(.+\))\}", requestData).group(1)  # 获取密码参数
            print("var_pass: %s" % var_pass)
            print("eval(var_pass): %s" % eval(var_pass))
            requestData = re.sub(r"\$\{\w+\(.+\)\}", eval(var_pass), requestData)  # 将requestBody里面的参数内容通过eval修改为实际变量值
            print("替换函数调用后，requestData: %s" % requestData)  # requestBody是拿到的请求时发送的数据

        if re.search(r"\$\{(\w+)\}", requestData):
            print("all mached data: %s" % (re.findall(r"\$\{(\w+)\}", requestData)))
            for var_name in re.findall(r"\$\{(\w+)\}", requestData):
                print("替换参数化变量之前 requestData: %s" % requestData)
                print("json.loads(os.environ['global_vars']): {}".format(json.loads(os.environ['global_vars'])))
                requestData = re.sub(r"\$\{%s\}" % var_name, str(json.loads(os.environ['global_vars'])[str(global_key)][var_name]), requestData)
                print("替换参数化变量之后 requestData: %s" % requestData )
        return 0, requestData, ""
    except Exception as e:
        print("数据处理发生异常，error：{}".format(traceback.format_exc()))
        return 1, {}, traceback.format_exc()





# #发送接口请求数据到接口的服务器 url 地址
# def send_request(interface_name, data):
#     data = data_handler(data)
#     try:
#         responseObj = api_request(eval(interface_name)[1], eval(interface_name)[0], eval(data))
#         return responseObj, data
#     except Exception as e:
#         print("调用接口的函数参数出错，调用的参数为%s" % interface_name, "\n错误信息: ", e)
#         return None, data


#断言处理，有多个断言词的情况
def assert_result(responseObj,key_word):
    '''验证数据正确性'''
    print('key_word in assert_result: {}'.format(key_word))

    try:
        if '&&' in key_word:
            key_word_list = key_word.split('&&')
            print("key_word_list: %s" % key_word_list)
            # 断言结果标识符
            flag = True
            # 遍历分隔出来的断言关键词列表
            for keyWord in key_word_list:
                if '"'in keyWord:
                    keyWord = keyWord.replace('"', "'")
                print("keyWord: %s" % keyWord)

                # 如果断言词非空，则进行断言
                if keyWord:
                    print("str(responseObj.json()): {}".format(str(responseObj.json())))
                    # 没查到断言词则认为是断言失败
                    if not (keyWord in str(responseObj.json())):
                        print("断言失败，关键词为： %s" % keyWord)
                        flag = False
                    else:
                        print("断言词匹配成功：'{}'".format(keyWord))
            print("flag: %s" % flag)
            if flag:
                print("断言成功")
            return flag

        else:
            print("key_word: %s" % key_word)
            if key_word in str(responseObj.json()):
                print("断言成功")
                return True
            else:
                print("断言失败，断言词为: %s" % key_word)
                return False
    except Exception as e:
        print("error occurs in assert_result function: %s" % e)
        return False



# 测试代码
if __name__ =="__main__":
    # logger.info("proj_path: ", proj_path)
    # logger.info("data_file: ", data_file)
    # #初始化2个唯一书变量，初始值可以根据数据的使用情况进行自定义
    #
    # data={"unique_num1":100,"unique_num2":1000}
    # with open(data_file,"wb") as fp:
    #     pickle.dump(data,fp) # 把data对象用pickle.dump()方法序列化到文件中存储
    # with open(data_file,"rb") as fp:
    #     data=pickle.load(fp) # 把文件中的内容用pickle.load()方法反序列化成python中的对象
    # logger.info("data: ", data)
    # logger.info('data["unique_num1"]: ', data["unique_num1"])
    # logger.info('data["unique_num2"]: ', data["unique_num2"])

    print(get_unique_number_value("unique_num1"))
    print(get_unique_number_value("unique_num2"))