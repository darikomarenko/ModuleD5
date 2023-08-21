import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
import datetime
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from ...models import Category, CategorySubscriber, Post
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def send_weekly_article_list():
    start_date = datetime.today() - timedelta(days=6)
    this_weeks_posts = Post.objects.filter(dateCreation__gt=start_date)
    for category in Category.objects.all():
        post_list = this_weeks_posts.filter(category=category)
        if post_list:
            subscribers = category.subscribers.all()
            context = {
                "post_list": post_list,
                "category": category,
            }

            for sub in subscribers:
                context["sub"] = sub
                html_content = render_to_string(
                    "weekly_article_list_email.html", context
                )

                msg = EmailMultiAlternatives(
                    subject=f"{category.name}: Посты за прошедшую неделю",
                    from_email="dariastore@yandex.ru",
                    to=[sub.email],
                )
                msg.attach_alternative(html_content, "text/html")
                # msg.send()
                print(html_content)


def delete_old_job_executions(scheduler, max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_article_list,
            trigger=CronTrigger(second="*/40"),
            id="send_weekly_article_list",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_article_list'.")

        delete_old_job_executions(scheduler)

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
