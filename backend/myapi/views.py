from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def tableau_url(request):
    # Replace the following URL with the actual URL of your Tableau dashboard
    data = {"url": "https://public.tableau.com/views/evses/EVSEDashboard"}
    return Response(data)
