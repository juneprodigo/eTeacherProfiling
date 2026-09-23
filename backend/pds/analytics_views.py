"""
pds/analytics_views.py — Teacher Analytics & Training Monitoring Hub APIs
Provides demographic breakdowns and training monitoring with dynamic filtering.
"""
from datetime import date
from django.db.models import Count, Sum, Avg, Q, Max
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsHROrAdmin
from .models import (
    Teacher,
    PersonalInfo,
    EducationalBackground,
    CivilServiceEligibility,
    WorkExperience,
    LearningDevelopment
)


class TeacherDemographicsAnalyticsView(APIView):
    """
    Returns demographic & professional distribution metrics across all registered teachers.
    Restricted to HR Officers and Admins.
    """
    permission_classes = [IsHROrAdmin]

    def get(self, request):
        dept_filter = request.query_params.get('department', '').strip()
        teachers_qs = Teacher.objects.filter(user__is_active=True).select_related('user', 'personal_info')

        if dept_filter:
            teachers_qs = teachers_qs.filter(department__icontains=dept_filter)

        total_teachers = teachers_qs.count()
        complete_pds = teachers_qs.filter(pds_complete=True).count()
        incomplete_pds = total_teachers - complete_pds
        pds_completion_rate = round((complete_pds / total_teachers * 100), 1) if total_teachers > 0 else 0

        # 1. Department Distribution
        dept_counts = (
            teachers_qs.exclude(department='')
            .values('department')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        departments = [
            {
                'name': d['department'],
                'count': d['count'],
                'percentage': round((d['count'] / total_teachers * 100), 1) if total_teachers > 0 else 0
            }
            for d in dept_counts
        ]

        # 2. Sex at Birth Distribution
        personal_infos = PersonalInfo.objects.filter(teacher__in=teachers_qs)
        sex_counts = personal_infos.values('sex_at_birth').annotate(count=Count('id'))
        sex_map = {'Male': 0, 'Female': 0, 'Unspecified': 0}
        for item in sex_counts:
            val = item['sex_at_birth']
            if val in sex_map:
                sex_map[val] = item['count']
            elif not val:
                sex_map['Unspecified'] += item['count']
            else:
                sex_map[val] = item['count']

        sex_distribution = [
            {
                'label': k,
                'count': v,
                'percentage': round((v / total_teachers * 100), 1) if total_teachers > 0 else 0
            }
            for k, v in sex_map.items() if v > 0 or k in ('Male', 'Female')
        ]

        # 3. Civil Status Distribution
        civil_counts = personal_infos.values('civil_status').annotate(count=Count('id')).order_by('-count')
        civil_distribution = [
            {
                'status': c['civil_status'] or 'Unspecified',
                'count': c['count'],
                'percentage': round((c['count'] / total_teachers * 100), 1) if total_teachers > 0 else 0
            }
            for c in civil_counts
        ]

        # 4. Age Bracket Demographics
        today = date.today()
        age_brackets = {
            'Under 30': 0,
            '30 - 39': 0,
            '40 - 49': 0,
            '50 - 59': 0,
            '60 and above': 0,
            'Unspecified': 0
        }
        for pi in personal_infos:
            if pi.date_of_birth:
                age = today.year - pi.date_of_birth.year - (
                    (today.month, today.day) < (pi.date_of_birth.month, pi.date_of_birth.day)
                )
                if age < 30:
                    age_brackets['Under 30'] += 1
                elif 30 <= age <= 39:
                    age_brackets['30 - 39'] += 1
                elif 40 <= age <= 49:
                    age_brackets['40 - 49'] += 1
                elif 50 <= age <= 59:
                    age_brackets['50 - 59'] += 1
                else:
                    age_brackets['60 and above'] += 1
            else:
                age_brackets['Unspecified'] += 1

        age_distribution = [
            {
                'bracket': k,
                'count': v,
                'percentage': round((v / total_teachers * 100), 1) if total_teachers > 0 else 0
            }
            for k, v in age_brackets.items() if v > 0 or k != 'Unspecified'
        ]

        # 5. Highest Educational Attainment
        edu_records = EducationalBackground.objects.filter(teacher__in=teachers_qs)
        # Check level counts
        level_counts = edu_records.values('level').annotate(count=Count('teacher', distinct=True)).order_by('-count')
        education_distribution = [
            {
                'level': e['level'],
                'count': e['count'],
                'percentage': round((e['count'] / total_teachers * 100), 1) if total_teachers > 0 else 0
            }
            for e in level_counts
        ]

        # 6. Civil Service Eligibility Types
        cse_records = CivilServiceEligibility.objects.filter(teacher__in=teachers_qs)
        cse_counts = cse_records.values('eligibility_type').annotate(count=Count('id')).order_by('-count')[:8]
        eligibility_distribution = [
            {'type': c['eligibility_type'], 'count': c['count']}
            for c in cse_counts
        ]

        # 7. Employment / Appointment Status from WorkExperience or Position
        work_records = WorkExperience.objects.filter(teacher__in=teachers_qs, to_present=True)
        appt_counts = work_records.values('appointment_status').annotate(count=Count('id')).order_by('-count')
        appointment_distribution = [
            {'status': a['appointment_status'] or 'Other', 'count': a['count']}
            for a in appt_counts if a['appointment_status']
        ]

        # List of departments for filter dropdown
        all_departments = list(
            Teacher.objects.exclude(department='').values_list('department', flat=True).distinct()
        )

        return Response({
            'total_teachers': total_teachers,
            'complete_pds': complete_pds,
            'incomplete_pds': incomplete_pds,
            'pds_completion_rate': pds_completion_rate,
            'departments': departments,
            'all_departments': all_departments,
            'sex_distribution': sex_distribution,
            'civil_distribution': civil_distribution,
            'age_distribution': age_distribution,
            'education_distribution': education_distribution,
            'eligibility_distribution': eligibility_distribution,
            'appointment_distribution': appointment_distribution,
        })


class TrainingMonitoringHubView(APIView):
    """
    Training & Seminar Monitoring Hub API with comprehensive multi-criteria filtering:
    - department
    - teacher_id
    - ld_type (Managerial, Technical, Supervisory, Foundational, Cross-Cutting)
    - year / date range
    - search (training_title, conducted_sponsored_by)
    - min_hours
    """
    permission_classes = [IsHROrAdmin]

    def get(self, request):
        trainings = LearningDevelopment.objects.select_related('teacher', 'teacher__user').all()

        # Query Filters
        dept = request.query_params.get('department', '').strip()
        teacher_id = request.query_params.get('teacher_id', '').strip()
        ld_type = request.query_params.get('ld_type', '').strip()
        year = request.query_params.get('year', '').strip()
        date_from = request.query_params.get('date_from', '').strip()
        date_to = request.query_params.get('date_to', '').strip()
        search = request.query_params.get('search', '').strip()
        min_hours = request.query_params.get('min_hours', '').strip()

        if dept:
            trainings = trainings.filter(teacher__department__icontains=dept)
        if teacher_id and teacher_id.isdigit():
            trainings = trainings.filter(teacher_id=int(teacher_id))
        if ld_type:
            trainings = trainings.filter(ld_type=ld_type)
        if year and year.isdigit():
            trainings = trainings.filter(
                Q(from_date__year=int(year)) | Q(to_date__year=int(year))
            )
        if date_from:
            trainings = trainings.filter(from_date__gte=date_from)
        if date_to:
            trainings = trainings.filter(to_date__lte=date_to)
        if search:
            trainings = trainings.filter(
                Q(training_title__icontains=search) | Q(conducted_sponsored_by__icontains=search)
            )
        if min_hours and min_hours.isdigit():
            trainings = trainings.filter(number_of_hours__gte=int(min_hours))

        # 1. High-Level KPIs
        agg_result = trainings.aggregate(
            total_hours=Sum('number_of_hours'),
            avg_hours=Avg('number_of_hours'),
            total_sessions=Count('id')
        )
        total_training_hours = agg_result['total_hours'] or 0
        avg_hours_per_session = round(agg_result['avg_hours'] or 0, 1)
        total_sessions = agg_result['total_sessions']

        # Total teachers in scope (based on department filter if provided)
        base_teachers = Teacher.objects.filter(user__is_active=True)
        if dept:
            base_teachers = base_teachers.filter(department__icontains=dept)
        total_faculty_count = base_teachers.count()

        distinct_teachers_trained = trainings.values('teacher').distinct().count()
        avg_hours_per_teacher = round(
            (total_training_hours / total_faculty_count), 1
        ) if total_faculty_count > 0 else 0

        # 2. Training Type Breakdown
        type_breakdown = (
            trainings.values('ld_type')
            .annotate(
                session_count=Count('id'),
                total_hours=Sum('number_of_hours')
            )
            .order_by('-total_hours')
        )
        ld_types_data = [
            {
                'type': item['ld_type'] or 'Uncategorized',
                'session_count': item['session_count'],
                'total_hours': item['total_hours'] or 0,
                'percentage': round(
                    ((item['total_hours'] or 0) / total_training_hours * 100), 1
                ) if total_training_hours > 0 else 0
            }
            for item in type_breakdown
        ]

        # 3. Faculty Training Compliance & Ranking
        # DepEd / CSC benchmark: 40 hours target for standard compliance
        TARGET_HOURS = 40
        teacher_stats = {}
        for t in base_teachers.select_related('user'):
            teacher_stats[t.id] = {
                'teacher_id': t.id,
                'name': t.user.get_full_name() or t.user.username,
                'employee_id': t.employee_id or '',
                'department': t.department or '',
                'total_hours': 0,
                'session_count': 0,
                'last_training_date': None,
                'status': 'No Records'
            }

        # Aggregate per teacher from filtered trainings
        teacher_aggs = (
            trainings.values('teacher_id')
            .annotate(
                hours=Sum('number_of_hours'),
                sessions=Count('id'),
                latest=Max('to_date')
            )
        )
        for ta in teacher_aggs:
            tid = ta['teacher_id']
            if tid in teacher_stats:
                h = ta['hours'] or 0
                teacher_stats[tid]['total_hours'] = h
                teacher_stats[tid]['session_count'] = ta['sessions']
                teacher_stats[tid]['last_training_date'] = ta['latest']
                if h >= TARGET_HOURS:
                    teacher_stats[tid]['status'] = 'Compliant'
                elif h > 0:
                    teacher_stats[tid]['status'] = 'In Progress'
                else:
                    teacher_stats[tid]['status'] = 'No Records'

        faculty_compliance = sorted(
            teacher_stats.values(),
            key=lambda x: (x['total_hours'], x['session_count']),
            reverse=True
        )

        compliant_count = sum(1 for f in faculty_compliance if f['status'] == 'Compliant')
        in_progress_count = sum(1 for f in faculty_compliance if f['status'] == 'In Progress')
        no_records_count = sum(1 for f in faculty_compliance if f['status'] == 'No Records')
        compliance_rate = round(
            (compliant_count / total_faculty_count * 100), 1
        ) if total_faculty_count > 0 else 0

        # 4. Detailed Training Records (limited to recent 100 for fast UI display)
        records = []
        for tr in trainings.order_by('-from_date')[:100]:
            records.append({
                'id': tr.id,
                'teacher_id': tr.teacher_id,
                'teacher_name': tr.teacher.user.get_full_name() or tr.teacher.user.username,
                'department': tr.teacher.department,
                'training_title': tr.training_title,
                'ld_type': tr.ld_type or 'General',
                'from_date': tr.from_date.isoformat() if tr.from_date else None,
                'to_date': tr.to_date.isoformat() if tr.to_date else None,
                'number_of_hours': tr.number_of_hours or 0,
                'conducted_sponsored_by': tr.conducted_sponsored_by or 'N/A'
            })

        # Available options for filters
        available_teachers = [
            {
                'id': t.id,
                'name': t.user.get_full_name() or t.user.username,
                'department': t.department
            }
            for t in base_teachers.select_related('user')
        ]
        available_years = list(
            LearningDevelopment.objects.exclude(from_date=None)
            .dates('from_date', 'year', order='DESC')
        )
        year_list = [d.year for d in available_years]

        return Response({
            'kpis': {
                'total_training_hours': total_training_hours,
                'avg_hours_per_session': avg_hours_per_session,
                'avg_hours_per_teacher': avg_hours_per_teacher,
                'total_sessions': total_sessions,
                'total_faculty_count': total_faculty_count,
                'distinct_teachers_trained': distinct_teachers_trained,
                'compliant_count': compliant_count,
                'in_progress_count': in_progress_count,
                'no_records_count': no_records_count,
                'compliance_rate': compliance_rate,
                'target_hours': TARGET_HOURS
            },
            'ld_types_breakdown': ld_types_data,
            'faculty_compliance': faculty_compliance,
            'records': records,
            'filter_options': {
                'teachers': available_teachers,
                'years': year_list,
                'departments': list(
                    Teacher.objects.exclude(department='').values_list('department', flat=True).distinct()
                ),
                'ld_types': [choice[0] for choice in LearningDevelopment.LDType.choices]
            }
        })
