from datetime import datetime, timedelta

from django.utils import timezone


def generate_time_slots(date, working_hours_dict):
    """
    Generate 30-minute slots based on working hours
    working_hours_dict: {'day': {'start': '09:00', 'end': '17:00'}}
    """
    day_name = date.strftime("%A").lower()
    hours = working_hours_dict.get(day_name)

    if not hours:
        return []

    work_start = timezone.make_aware(
        datetime.strptime(f"{date.date()} {hours['start']}", "%Y-%m-%d %H:%M")
    )
    work_end = timezone.make_aware(
        datetime.strptime(f"{date.date()} {hours['end']}", "%Y-%m-%d %H:%M")
    )

    slots = []
    current = work_start

    while current < work_end:
        slots.append(current)
        current += timedelta(minutes=30)

    return slots


def validate_appointment_time(start_time, end_time, working_hours_list):
    """
    Validate appointment time against working hours list
    working_hours_list: List of WorkingHours objects
    """
    day_name = start_time.strftime("%A").lower()

    for working_hours in working_hours_list:
        if working_hours.day_of_week != day_name:
            continue

        work_start = timezone.make_aware(
            datetime.combine(start_time.date(), working_hours.start_time)
        )
        work_end = timezone.make_aware(
            datetime.combine(start_time.date(), working_hours.end_time)
        )

        if work_start <= start_time < end_time <= work_end:
            return True, "Valid"

    return False, "Outside doctor's working hours"
