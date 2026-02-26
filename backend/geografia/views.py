from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Provincia, Localidad
from .serializers import ProvinciaSerializer, LocalidadSerializer


class ProvinciaList(APIView):
    def get(self, request):
        provincias = Provincia.objects.all()
        serializer = ProvinciaSerializer(provincias, many=True)
        return Response(serializer.data)


class LocalidadPorProvincia(APIView):
    def get(self, request):
        provincia_id = request.query_params.get("provincia")

        if not provincia_id:
            return Response({"error": "Falta provincia"}, status=400)

        localidades = Localidad.objects.filter(
            departamento__provincia_id=provincia_id
        )

        serializer = LocalidadSerializer(localidades, many=True)
        return Response(serializer.data)