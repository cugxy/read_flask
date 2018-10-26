# Flask 源码解析
|> cugxy
 
源码版本为 8605cc31, `git clone git@github.com:pallets/flask.git; git checkout 8605cc31 `，同时由于 werkzeug 的更新，代码运行是肯定不能运行的，需要修改部分 import ，这里我已经改好，且添加了例子。直接看这份代码即可。
# 大纲
## 困惑
1. ### Flask 类与 WSGI 的关系
   
2. ### run() 函数
3. ### 路由-视图函数的添加
4. ### 路由-视图函数的触发
## 难题
- ### 全局线程安全变量 ` current_app, request, session `

# 解析
## Flaks 类与 WSGI 的关系
    WSGI ([详情](https://wsgi.readthedocs.io/en/latest/what.html))首先是一个协议，协议里约定了 web 服务器如何调用 web 应用程序，以及 web 应用程序需要遵守怎样的规范。也就是说，任何实现了 WSGI 的web 服务器与 web 应用程序都可以随意搭配。

    Flask 类就是一个遵守了 WSGI 协议的 web 应用程序框架。
#### Flask 类主要成员变量

- ` view_functions ` 字典
  
- ` error_handlers ` 字典
- ` before_request_funcs ` 列表
- ` after_request_funcs ` 列表
- ` url_map `  Map 对象
  
` __call__() ` 函数，确保 Flask 对象是可执行的。（不了解 ` __call__() ` 的点击 --> [python 魔法方法](https://pyzh.readthedocs.io/en/latest/python-magic-methods-guide.html)）

## run() 函数
    调用 werkzeng 中 run_simple() 函数，并讲遵守了 WSGI 协议的 self 传入，则 werkzeng 将启动 web 服务，并在服务所监听的端口接收到请求时，按照 WSGI 协议调用 self ，即调用 Flask.__call__() 方法。

## 路由-视图函数的添加
路由函数添加依赖于 python 注解机制。（不了解 注解机制 的点击 --> [python 注解](https://www.jianshu.com/p/7a644520418b)）Flask 中定义的 ` route ` 注解如下:
```
def route(self, rule, **options):
    def decorator(f):
        self.add_url_rule(rule, f.__name__, **options)
        self.view_functions[f.__name__] = f
        return f
    return decorator
```
将路由于视图函数一起加入到 ` url_map ` 中，并为字典 `view_functions` 赋值。记录下视图函数。

## 路由-视图函数的触发
在服务所监听的端口接收到请求时，按照 WSGI 协议调用 werkzeng 服务将调用 `__call__()` 方法，且将参数 `environ` (其中包含有关请求的所有信息，如 path, host, port,user_agent, cookie 等等)，`__call__()` 则会调用 `wsgi_app()` 通过  `url_map`, `view_functions`, `view_functions`, `view_functions` 等成员变量依次处理，调用视图函数并打包结果返回。其中最重要的 `match_request` 函数找到视图函数 `dispatch_request`调用视图函数并包装结果。

## 全局线程安全变量 ` current_app, request, session `
其实该功能的实现只有以下几行代码：
```
_request_ctx_stack = LocalStack()
current_app = LocalProxy(lambda: _request_ctx_stack.top.app)
request = LocalProxy(lambda: _request_ctx_stack.top.request)
session = LocalProxy(lambda: _request_ctx_stack.top.session)
```
其中 `LocalStack` 类只有成员变量，`_local` 为 `Local` 类对象。`Local` 类有如下属性：

(不了解 ` __slots__() ` 的点击 --> [python __slots__魔法](https://eastlakeside.gitbooks.io/interpy-zh/content/slots_magic/))

(不了解 协程 的点击 --> [python 协程](https://eastlakeside.gitbooks.io/interpy-zh/content/Coroutines/))
- `__storage__`：用户存储的字典，且 key 为线程或协程 id
- `__ident_func__`： 用户获取当前线程或协程 id
  
LocalStack 则为一个栈，用于线程安全的取出当前线程或协程对应的变量。
