from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import models
from .utils.api_request import api_request
from .utils.dataHandler import data_handler, assert_result
import os
import json
import traceback
import time
from dateutil.parser import parse

# ip = "39.100.104.214"
# port = "8000"

@shared_task
def interface_test_task(test_case_id_list, server_address):
    global_key = int(time.time()*100000)
    global_vars = {"{}".format(global_key): {}}
    os.environ['global_vars'] = json.dumps(global_vars)
    for test_case_id in test_case_id_list:
        test_case = models.TestCase.objects.filter(id=int(test_case_id))[0]
        print("######执行用例: {}".format(test_case))
        last_execute_record_data = models.TestCaseExecuteRecord.objects.filter(
            belong_test_case_id=test_case_id).order_by('-id')
        if last_execute_record_data:
            last_time_execute_response_data = last_execute_record_data[0].response_data
        else:
            last_time_execute_response_data = ''
        print("last_execute_record_data: {}".format(last_execute_record_data))
        print("last_time_execute_response_data: {}".format(last_time_execute_response_data))
        execute_record = models.TestCaseExecuteRecord.objects.create(belong_test_case=test_case)
        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        print("execute_start_time: {}".format(execute_start_time))
        execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
        print("execute_record.execute_start_time: {}".format(execute_record.execute_start_time))
        execute_record.last_time_response_data = last_time_execute_response_data
        # 获取当前用例上一次执行结果
        execute_record.save()
        '''
        interface_name = models.CharField('接口名称', max_length=50, null=False)  # register
        belong_project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目')
        belong_module = GroupedForeignKey(Module, "belong_project", on_delete=models.CASCADE, verbose_name='所属模块')
        request_data = models.CharField('请求数据', max_length=1024, null=False)
        assert_key = models.CharField('断言内容', max_length=1024, null=True)
        maintainer = models.CharField('编写人员', max_length=1024, null=False)
        extract_var = models.CharField('提取变量表达式', max_length=1024, null=True)  # userid||userid": (\d+)
        if_execute = models.CharField('是否执行', max_length=1024, null=False)
        status = models.IntegerField(null=True, help_text="0：表示有效，1：表示无效，用于软删除")
        created_time = models.DateTimeField('创建时间', auto_now_add=True)
        updated_time = models.DateTimeField('更新时间', auto_now=True, null=True)
        user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户', null=True)
    
        '''
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("request_data: {}".format(test_case.request_data))
        print("extract_var: {}".format(extract_var))
        print("assert_key: {}".format(assert_key))
        print("interface_name: {}".format(interface_name))
        print("belong_project: {}".format(belong_project))
        print("belong_module: {}".format(belong_module))
        print("maintainer: {}".format(maintainer))
        print("request_method: {}".format(request_method))
        url = "{}/{}".format(server_address, interface_name)
        print("url: {}".format(url))
        code, request_data, error_msg = data_handler(global_key, str(request_data))
        print("request_data: {}".format(request_data))
        if code != 0:
            print("数据处理异常，error: {}".format(error_msg))
            execute_record.execute_result = "失败"
            execute_record.status = 1
            execute_record.exception_info = error_msg
            execute_end_time = time.time()
            execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
            execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
            execute_record.save()
        execute_record.request_data = request_data
        try:
            res_data = api_request(url, request_method, json.loads(request_data))
            print("res_data.json(): {}".format(res_data.json()))

            result_code, exception_info  = assert_result(res_data, assert_key)
            if result_code:
                print("用例执行成功")
                execute_record.execute_result = "成功"
                execute_record.response_data = res_data.json()
                execute_record.status = 1
                execute_end_time = time.time()
                print("execute_end_time: {}".format(execute_end_time))
                execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
                print("int((execute_end_time - execute_start_time) * 1000): {}".format(int((execute_end_time - execute_start_time) * 1000)))
                execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
                print("execute_record.execute_total_time.microseconds: {}".format(execute_record.execute_total_time))
                execute_record.save()
            else:
                print("用例执行失败")
                execute_record.execute_result = "失败"
                execute_record.response_data = res_data.json()
                execute_record.exception_info = exception_info
                execute_record.status = 1
                execute_end_time = time.time()
                execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
                execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
                print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
                execute_record.save()
        except Exception as e:
            print("接口请求异常，error: {}".format(e))
            execute_record.execute_result = "失败"
            execute_record.exception_info = e
            execute_record.status = 1
            execute_end_time = time.time()
            execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("execute_record.execute_end_time: {}".format(execute_record.execute_end_time))
            execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("execute_record.execute_total_time: {}".format(execute_record.execute_total_time))
            execute_record.save()


# @shared_task
def web_suit_task(test_suit_record, test_suit):
    global_vars = {"{}".format(test_suit_record.id): {}}
    os.environ['global_vars'] = json.dumps(global_vars)
    server_address = "http://39.100.104.214:8000"
    test_suit_test_cases = models.TestSuitTestCases.objects.filter(test_suit=test_suit).order_by('id')
    print("test_suit_test_cases: {}".format(test_suit_test_cases))
    test_suit_record.test_result = "成功"
    test_suit_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    for test_suit_test_case in test_suit_test_cases:
        test_case = test_suit_test_case.test_case
        print("######执行用例: {}".format(test_case))
        last_execute_record_data = models.TestSuitTestCaseExecuteRecord.objects.filter(
            test_case_id=test_case.id).order_by('-id')
        if last_execute_record_data:
            last_time_execute_response_data = last_execute_record_data[0].response_data
        else:
            last_time_execute_response_data = ''
        print("last_execute_record_data: {}".format(last_execute_record_data))
        print("last_time_execute_response_data: {}".format(last_time_execute_response_data))
        suite_case_execute_record = models.TestSuitTestCaseExecuteRecord.objects.create(test_suit_record=test_suit_record,
                                                                             test_case=test_case)
        execute_start_time = time.time()  # 记录时间戳，便于计算总耗时（毫秒）
        print("execute_start_time: {}".format(execute_start_time))
        suite_case_execute_record.execute_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_start_time))
        print("suite_case_execute_record.execute_start_time: {}".format(suite_case_execute_record.execute_start_time))
        suite_case_execute_record.last_time_response_data = last_time_execute_response_data
        suite_case_execute_record.save()
        request_data = test_case.request_data
        extract_var = test_case.extract_var
        assert_key = test_case.assert_key
        interface_name = test_case.uri
        belong_project = test_case.belong_project
        belong_module = test_case.belong_module
        maintainer = test_case.maintainer
        request_method = test_case.request_method
        print("request_data: {}".format(test_case.request_data))
        print("extract_var: {}".format(extract_var))
        print("assert_key: {}".format(assert_key))
        print("interface_name: {}".format(interface_name))
        print("belong_project: {}".format(belong_project))
        print("belong_module: {}".format(belong_module))
        print("maintainer: {}".format(maintainer))
        print("request_method: {}".format(request_method))
        url = "{}/{}".format(server_address, interface_name)
        print("url: {}".format(url))
        code, request_data, error_msg = data_handler(test_suit_record.id, str(request_data))
        print("request_data: {}".format(request_data))
        if code != 0:
            print("数据处理异常，error: {}".format(error_msg))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.status = 1
            suite_case_execute_record.exception_info = error_msg
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

        suite_case_execute_record.request_data = request_data
        try:
            res_data = api_request(url, request_method, json.loads(request_data))
            print("res_data.json(): {}".format(res_data.json()))
            if assert_result(res_data, assert_key):
                # if res_data.json().get("code", "") == "00":
                print("用例执行成功")
                suite_case_execute_record.execute_result = "成功"
                suite_case_execute_record.response_data = res_data.json()
                suite_case_execute_record.status = 1
                execute_end_time = time.time()
                print("execute_end_time: {}".format(execute_end_time))
                suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
                print("int((execute_end_time - execute_start_time) * 1000): {}".format(
                    int((execute_end_time - execute_start_time) * 1000)))
                suite_case_execute_record.execute_total_time = int((execute_end_time - execute_start_time) * 1000)
                print("suite_case_execute_record.execute_total_time.microseconds: {}".format(suite_case_execute_record.execute_total_time))
                suite_case_execute_record.save()

            else:
                print("用例执行失败")
                suite_case_execute_record.execute_result = "失败"
                suite_case_execute_record.response_data = res_data.json()
                suite_case_execute_record.status = 1
                execute_end_time = time.time()
                suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
                print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
                suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
                print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
                suite_case_execute_record.save()
                test_suit_record.test_result = "失败"
        except Exception as e:
            print("接口请求异常，error: {}".format(e))
            suite_case_execute_record.execute_result = "失败"
            suite_case_execute_record.exception_info = e
            suite_case_execute_record.status = 1
            execute_end_time = time.time()
            suite_case_execute_record.execute_end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(execute_end_time))
            print("suite_case_execute_record.execute_end_time: {}".format(suite_case_execute_record.execute_end_time))
            suite_case_execute_record.execute_total_time = int(execute_end_time - execute_start_time) * 1000
            print("suite_case_execute_record.execute_total_time: {}".format(suite_case_execute_record.execute_total_time))
            suite_case_execute_record.save()
            test_suit_record.test_result = "失败"

    test_suit_record.status = 1  # 执行完了
    test_suit_record.save()