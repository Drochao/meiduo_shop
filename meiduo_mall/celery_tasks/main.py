from celery import Celery


# 1.创建celery客户端对象
celery_app = Celery('meiduo')

# 2.加载celery的配置，让生产者知道自己生产的任务存放到哪？
celery_app.config_from_object('celery_tasks.config')

# 3，自动注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])