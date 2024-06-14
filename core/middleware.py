from admin_reorder.middleware import ModelAdminReorder


class ModelAdminReorderWithNav(ModelAdminReorder):
    def process_template_response(self, request, response):
        if (
            getattr(response, "context_data", None)
            and not response.context_data.get("app_list")
            and (available_apps := response.context_data.get("available_apps"))
        ):
            response.context_data["app_list"] = available_apps
            response = super().process_template_response(request, response)
            response.context_data["available_apps"] = response.context_data["app_list"]
            return response

        return super().process_template_response(request, response)
