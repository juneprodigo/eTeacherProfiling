from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from .models import SchoolActivity, ActivityParticipant
from .serializers import SchoolActivitySerializer, ActivityParticipantSerializer
from accounts.permissions import IsHROrAdmin
from pds.models import Teacher


class SchoolActivityViewSet(viewsets.ModelViewSet):
    queryset = SchoolActivity.objects.select_related('coordinator__user').prefetch_related(
        'participants__teacher__user'
    ).all()
    serializer_class = SchoolActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        type_param = self.request.query_params.get('activity_type')
        modality_param = self.request.query_params.get('modality')
        coordinator_param = self.request.query_params.get('coordinator')
        search = self.request.query_params.get('search')

        if status_param:
            qs = qs.filter(status=status_param)
        if type_param:
            qs = qs.filter(activity_type=type_param)
        if modality_param:
            qs = qs.filter(modality=modality_param)
        if coordinator_param:
            qs = qs.filter(coordinator_id=coordinator_param)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(venue__icontains=search) |
                Q(funding_source__icontains=search)
            )
        return qs

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Aggregate statistical metrics for activities monitoring hub."""
        now = timezone.now()
        total_activities = SchoolActivity.objects.count()
        upcoming = SchoolActivity.objects.filter(status='Upcoming').count()
        in_progress = SchoolActivity.objects.filter(status='In Progress').count()
        completed = SchoolActivity.objects.filter(status='Completed').count()
        total_budget = SchoolActivity.objects.aggregate(total=Sum('budget'))['total'] or 0.00

        total_participations = ActivityParticipant.objects.count()
        attended_participations = ActivityParticipant.objects.filter(attendance_status='Attended').count()
        attendance_rate = (
            round((attended_participations / total_participations) * 100, 1)
            if total_participations > 0 else 0
        )

        type_breakdown = (
            SchoolActivity.objects.values('activity_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        modality_breakdown = (
            SchoolActivity.objects.values('modality')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'total_activities': total_activities,
            'upcoming': upcoming,
            'in_progress': in_progress,
            'completed': completed,
            'total_budget': float(total_budget),
            'total_participations': total_participations,
            'attended_participations': attended_participations,
            'attendance_rate': attendance_rate,
            'type_breakdown': list(type_breakdown),
            'modality_breakdown': list(modality_breakdown),
        })

    @action(detail=True, methods=['post'], url_path='participants')
    def add_participant(self, request, pk=None):
        activity = self.get_object()
        teacher_id = request.data.get('teacher_id')
        role = request.data.get('role', 'Participant')
        attendance_status = request.data.get('attendance_status', 'Registered')

        if not teacher_id:
            return Response({'error': 'teacher_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)

        participant, created = ActivityParticipant.objects.get_or_create(
            activity=activity,
            teacher=teacher,
            defaults={'role': role, 'attendance_status': attendance_status}
        )
        if not created:
            participant.role = role
            participant.attendance_status = attendance_status
            participant.save()

        return Response(ActivityParticipantSerializer(participant).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path=r'participants/(?P<part_id>\d+)')
    def participant_detail(self, request, pk=None, part_id=None):
        activity = self.get_object()
        try:
            participant = activity.participants.get(pk=part_id)
        except ActivityParticipant.DoesNotExist:
            return Response({'error': 'Participant record not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            participant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = ActivityParticipantSerializer(participant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='batch-attendance')
    def batch_attendance(self, request, pk=None):
        """Batch update attendance statuses: updates list of {id: X, attendance_status: 'Attended'}."""
        activity = self.get_object()
        updates = request.data.get('updates', [])
        for item in updates:
            part_id = item.get('id')
            new_status = item.get('attendance_status')
            cert = item.get('certificate_issued')
            if part_id:
                p_qs = activity.participants.filter(pk=part_id)
                update_fields = {}
                if new_status:
                    update_fields['attendance_status'] = new_status
                if cert is not None:
                    update_fields['certificate_issued'] = cert
                if update_fields:
                    p_qs.update(**update_fields)

        return Response({'message': 'Attendance updated successfully.'})
