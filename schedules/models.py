from django.db import models

from doctors.models import Doctor


class WorkingHours(models.Model):
    DAYS_OF_WEEK = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
    ]

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="working_hours"
    )
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = ["doctor", "day_of_week"]
        indexes = [
            models.Index(fields=["doctor", "day_of_week", "is_available"]),
        ]

    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise models.ValidationError("Start time must be before end time")
