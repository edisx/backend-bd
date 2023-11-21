from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes

from api.serializers import ActionLogSerializer
from api.models import ActionLog

from rest_framework import status
from api.permissions import IsSuperUser

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsSuperUser])
def getActionLogs(request):
    """
    Retrieve all action logs from the database and return them as a response.

    Args:
        request: The HTTP request object.

    Returns:
        A Response object containing the serialized data of all action logs.
        If an exception occurs, a Response object with an error message and
        status code 500 will be returned.
    """
    try:
        actionLogs = ActionLog.objects.all().order_by('-id')

        page = request.query_params.get("page")
        paginator = Paginator(actionLogs, 10) # n items per page

        try:
            actionLogs = paginator.page(page)
        except PageNotAnInteger:
            actionLogs = paginator.page(1)
        except EmptyPage:
            actionLogs = paginator.page(paginator.num_pages)

        if page is None:
            page = 1

        page = int(page)

        serializer = ActionLogSerializer(actionLogs, many=True)
        return Response({'actionLogs': serializer.data, 'page': page, 'pages': paginator.num_pages}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )