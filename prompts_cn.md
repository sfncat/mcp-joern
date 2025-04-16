## 信息
1. cpg_filepath = /home/user/cpg/com.android.nfc.cpg  
2. class_full_name = com.android.nfc.NfcService$6
## 处理要求
1. 查看当前class下的onReceive方法的代码，分析代码逻辑，查看针对不同的Action的处理逻辑。
2. 如果不同Action的处理调用其它方法，继续查看调用的方法的代码,如果有需要,可以继续分析后续调用的方法。
3. 针对有安全风险的Action处理,描述完整的的处理逻辑,关注是否从intent中获取了参数,以及对参数的处理,关注是否有敏感操作或敏感信息。
4. 如果存在安全漏洞，详细描述可能的安全漏洞原因,给出漏洞相关代码,生成可以走到漏洞分支的Intent数据
5. 如果在处理逻辑中进行了日志打印,找出打印的TAG字符串
## 注意事项
1. joern server已经启动  
2. joern mcp server已经启动  
3. joern中字符串需要使用双引号，而不是单引号
## 净化规则
1. 不需要考虑权限校验
2. 不需要考虑验证Intent来源
## 输出规则
1. 输出使用markdown格式  
2. 构造的intent数据使用java语言表示  
3. 使用中文回答