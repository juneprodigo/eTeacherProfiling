from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def create_user_teacher_profile(sender, instance, created, **kwargs):
    from pds.models import Teacher
    from attendance.models import LeaveBalance
    
    teacher = getattr(instance, 'teacher_profile', None)
    if not teacher:
        dept = 'Administration' if instance.role == 'admin' else ('Human Resources' if instance.role == 'hr' else 'Faculty Department')
        pos = 'School Administrator' if instance.role == 'admin' else ('HR Officer' if instance.role == 'hr' else 'Faculty Teacher')
        emp_id = f'DEPED-{instance.role.upper()[:3]}-{instance.id:04d}'
        teacher, _ = Teacher.objects.get_or_create(
            user=instance,
            defaults={
                'employee_id': emp_id,
                'department': dept,
                'position': pos,
            }
        )

    try:
        LeaveBalance.objects.get_or_create(teacher=teacher)
    except Exception:
        pass
