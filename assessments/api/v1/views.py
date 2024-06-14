import operator
from functools import reduce

from django_filters import CharFilter, FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.compat import distinct
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from ...applogic import rating_applogic, summary_applogic
from ...models import ComplianceCriticalityAssessment, ReviewComment
from .serializers import (
    ComplianceCriticalityAssessmentListSerializer,
    ComplianceCriticalityAssessmentSerializer,
    ComplianceCriticalityAssessmentSummarySerializer,
    ReviewCommentInputSerializer,
    ReviewCommentSerializer,
)


class CcaFilterSet(FilterSet):
    status = CharFilter(method="filter_status")
    solution_type = CharFilter(method="filter_solution_type")
    solution_classification = CharFilter(method="filter_solution_classification")
    hosting_and_type = CharFilter(method="filter_hosting_and_type")

    def filter_status(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(status__in=values)

    def filter_solution_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(solution_type__in=values)

    def filter_solution_classification(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(solution_classification__in=values)

    def filter_hosting_and_type(self, queryset, name, value):
        values = value.split(",")
        return queryset.filter(hosting_and_type__in=values)


class CCASearchFilter(filters.SearchFilter):
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, "")
        params = params.replace("\x00", "")  # strip null characters
        params = params.replace(",", " ")
        return params


class CcaApiModelViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        CCASearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CcaFilterSet
    search_fields = ["solution_name", "name"]
    ordering_fields = ["-created"]

    def get_serializer_class(self):
        if self.action == "list":
            return ComplianceCriticalityAssessmentListSerializer
        return ComplianceCriticalityAssessmentSerializer

    def get_queryset(self):
        # suppress log error on api docs for unauthenticated access
        # to request.user.company
        if self.request.user.is_authenticated:
            user_company = self.request.user.company

            if user_company:
                queryset = ComplianceCriticalityAssessment.objects.filter(
                    company=user_company
                )

                return queryset.order_by("-created")

        return ComplianceCriticalityAssessment.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user

        return context

    def create(self, request):
        response = {"message": "Not Implemented."}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        response = {"message": "Not Implemented."}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        # status is set to draft on update unless "draft" key is False
        # Then it is set to For Review which is considered as submit
        res = super().update(request, *args, **kwargs)
        user = request.user
        instance = self.get_object()

        if request.data.get("draft", True):
            instance = instance.transition_to_draft()
        else:
            # if the person who submitted the form is also one of the approvers,
            # automatically set their approved_by to True
            instance = instance.transition_to_for_review(prev_status=instance.status)

            match user:
                case instance.business_owner:
                    instance.approved_by_business_owner = True
                    instance.datetime_approved_by_business_owner = timezone.now()
                    instance.save(
                        update_fields=[
                            "approved_by_business_owner",
                            "datetime_approved_by_business_owner",
                        ]
                    )
                case instance.system_owner:
                    instance.approved_by_system_owner = True
                    instance.datetime_approved_by_system_owner = timezone.now()
                    instance.save(
                        update_fields=[
                            "approved_by_system_owner",
                            "datetime_approved_by_system_owner",
                        ]
                    )
                case instance.it_risk_management_and_compliance:
                    instance.approved_by_it_risk_management_and_compliance = True
                    instance.datetime_approved_by_it_risk_management_and_compliance = (
                        timezone.now()
                    )
                    instance.save(
                        update_fields=[
                            "approved_by_it_risk_management_and_compliance",
                            "datetime_approved_by_it_risk_management_and_compliance",
                        ]
                    )
                case _:
                    pass

        # update the res.data with the latest instance
        serializer = self.get_serializer_class()
        res.data = serializer(instance).data
        return res

    def retrieve(self, request, *args, **kwargs):
        instance: ComplianceCriticalityAssessment = self.get_object()
        if request.user.company != instance.company:
            return Response(
                {"error": "User has no permission to access this record."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = ComplianceCriticalityAssessmentSerializer(instance)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="comments")
    def comments(self, request, pk):
        instance: ComplianceCriticalityAssessment = self.get_object()
        serializer = ReviewCommentSerializer(
            instance.comments.order_by("-created"), many=True
        )
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_cca(self, request, pk):
        user = request.user
        instance: ComplianceCriticalityAssessment = self.get_object()
        match user:
            case instance.business_owner:
                instance.approved_by_business_owner = True
                instance.datetime_approved_by_business_owner = timezone.now()
                approver = "Business Owner"
            case instance.system_owner:
                instance.approved_by_system_owner = True
                instance.datetime_approved_by_system_owner = timezone.now()
                approver = "System Owner"
            case instance.it_risk_management_and_compliance:
                instance.approved_by_it_risk_management_and_compliance = True
                instance.datetime_approved_by_it_risk_management_and_compliance = (
                    timezone.now()
                )
                approver = "It Risk Management And Compliance"
            case _:
                return Response(
                    {"error": "User is not part of the approval team."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        instance.save()
        return Response(
            {
                "success": f"Successfully approved as {approver}",
                "data": ComplianceCriticalityAssessmentSerializer(instance).data,
            },
            status.HTTP_202_ACCEPTED,
        )

    @swagger_auto_schema(request_body=ReviewCommentInputSerializer)
    @action(
        detail=True,
        methods=["post"],
        url_path="reject",
    )
    def reject_cca(self, request, pk):
        user = request.user
        instance: ComplianceCriticalityAssessment = self.get_object()
        match user:
            case instance.business_owner:
                instance.approved_by_business_owner = False
                instance.datetime_approved_by_business_owner = None
                approver = "Business Owner"
            case instance.system_owner:
                instance.approved_by_system_owner = False
                instance.datetime_approved_by_system_owner = None
                approver = "System Owner"
            case instance.it_risk_management_and_compliance:
                instance.approved_by_it_risk_management_and_compliance = False
                instance.datetime_approved_by_it_risk_management_and_compliance = None
                approver = "It Risk Management And Compliance"
            case _:
                return Response(
                    {"error": "User is not part of the approval team."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        instance.save()

        if comment_serializer := ReviewCommentInputSerializer(data=request.data):
            if comment_serializer.is_valid(raise_exception=True):
                if comment := comment_serializer.validated_data.get("comment"):
                    ReviewComment.objects.create(
                        comment=comment,
                        user=request.user,
                        cca=instance,
                    )

        return Response(
            {
                "success": f"Successfully rejected as {approver}",
                "data": ComplianceCriticalityAssessmentSerializer(instance).data,
            },
            status.HTTP_202_ACCEPTED,
        )

    @swagger_auto_schema(request_body=ComplianceCriticalityAssessmentSummarySerializer)
    @action(
        detail=False,
        methods=["post"],
        url_path="summary",
    )
    def summary(self, request):
        serializer = ComplianceCriticalityAssessmentSummarySerializer(data=request.data)
        if serializer.is_valid():
            try:
                summary = summary_applogic.calculate_summary(serializer.data)
                rating = rating_applogic.calculate_rating(summary)
                data = {
                    "summary": summary,
                    "rating": rating,
                }
                return Response(data, status=status.HTTP_202_ACCEPTED)
            except ValidationError as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
