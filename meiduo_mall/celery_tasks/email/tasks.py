import logging
from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


logger = logging.getLogger('send_email')
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   f'<p>您的邮箱为：{to_email} 。请点击此链接激活您的邮箱：</p>' \
                   f'<p><a href="{verify_url}">{verify_url}<a></p>'

    try:
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)

        raise self.retry(exc=e, max_retries=3)
