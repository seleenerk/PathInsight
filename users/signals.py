from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import JobPosting, MatchResult, JobApplication

@receiver(post_delete, sender=JobPosting)
def delete_related_data_on_job_delete(sender, instance, **kwargs):
    MatchResult.objects.filter(job=instance).delete()
    JobApplication.objects.filter(job=instance).delete()
