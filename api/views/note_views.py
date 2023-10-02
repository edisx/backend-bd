from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.serializers import NoteSerializer
from api.models import Note

@api_view(['GET'])
def getNotes(request):
    notes = Note.objects.all()
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data)



