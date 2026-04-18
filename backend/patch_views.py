import re

with open("apps/mtm/views.py", "r") as f:
    content = f.read()

# Add _build_initial_plan_payload and _get_or_create_plan
insert_plan_methods = """
    def _build_initial_plan_payload(self, service_case):
        return {
            "service_case": service_case,
            "interventions": [],
            "priority": "medium",
            "patient_confirmation_status": "pending",
            "patient_confirmation_notes": "",
        }

    def _get_or_create_plan(self, service_case):
        plan, created = MTMPlan.objects.get_or_create(
            service_case=service_case,
            defaults=self._build_initial_plan_payload(service_case),
        )
        if created:
            logger.info(
                "🟢 [MTM] plan draft initialized - case=%s plan=%s",
                service_case.id,
                plan.id,
            )
        return plan
"""

if "_get_or_create_plan" not in content:
    content = content.replace("def get_queryset(self):", insert_plan_methods + "\n    def get_queryset(self):")


# Add action endpoints
insert_plan_actions = """
    @action(detail=True, methods=["get", "put"])
    def plan(self, request, pk=None):
        service_case = self.get_object()
        plan = self._get_or_create_plan(service_case)

        if request.method == "GET":
            logger.info("🔵 [MTM] plan fetch - case=%s plan=%s", service_case.id, plan.id)
            serializer = MTMPlanSummarySerializer(plan)
            return success_response(data=serializer.data)

        if request.method == "PUT":
            from .serializers import MTMPlanDraftSerializer
            serializer = MTMPlanDraftSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message="保存草稿失败", errors=serializer.errors)

            for field, value in serializer.validated_data.items():
                setattr(plan, field, value)
            plan.save()
            logger.info("🟢 [MTM] plan draft saved - case=%s", service_case.id)
            return success_response(data=MTMPlanSummarySerializer(plan).data)

    @action(detail=True, methods=["post"], url_path="plan/complete")
    def complete_plan(self, request, pk=None):
        service_case = self.get_object()
        plan = self._get_or_create_plan(service_case)

        from .serializers import MTMPlanCompleteSerializer
        serializer = MTMPlanCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="完成计划失败，数据不完整", errors=serializer.errors)

        with transaction.atomic():
            for field, value in serializer.validated_data.items():
                setattr(plan, field, value)
            # If they pass confirmed_at or we want to record it? Not required for completion of form.
            plan.save()

            if service_case.status == "assessing":
                service_case.transition_to("intervening", note="干预计划已制定，自动进入干预阶段")
            
        logger.info("🟢 [MTM] plan completed - case=%s", service_case.id)
        return success_response(data=MTMPlanSummarySerializer(plan).data)

    @action(detail=True, methods=["get", "post"], url_path="follow-ups")
    def follow_ups(self, request, pk=None):
        service_case = self.get_object()

        if request.method == "GET":
            follow_ups = service_case.follow_ups.all().order_by("-follow_up_time")
            from .serializers import MTMFollowUpSummarySerializer
            return success_response(data=MTMFollowUpSummarySerializer(follow_ups, many=True).data)

        if request.method == "POST":
            from .serializers import MTMFollowUpFormSerializer
            serializer = MTMFollowUpFormSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message="保存随访记录失败", errors=serializer.errors)

            follow_up = serializer.save(service_case=service_case)
            logger.info("🟢 [MTM] follow-up created - case=%s id=%s", service_case.id, follow_up.id)
            
            # 自动流转：如果处于 intervening 且有随访记录，可以自动进入 follow_up 阶段
            if service_case.status == "intervening":
                service_case.transition_to("follow_up", note="随访记录已创建，自动进入随访阶段")

            from .serializers import MTMFollowUpSummarySerializer
            return success_response(data=MTMFollowUpSummarySerializer(follow_up).data)
"""

if "def complete_plan" not in content:
    content = content + "\n" + insert_plan_actions

with open("apps/mtm/views.py", "w") as f:
    f.write(content)
